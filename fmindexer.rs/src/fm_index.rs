use std::io;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct FMIndex {
    bwt: Vec<u8>,
    alphabet: Vec<u8>,
    occ: Vec<u32>,
    counts: Vec<u32>,
    sarray: Vec<u32>,
}

impl FMIndex {
    fn get_idx(alphabet: &[u8], x: u8) -> usize {
        for (i, &c) in alphabet.iter().enumerate() {
            if x == c {
                return i;
            }
        }

        panic!("Somehow get_idx({x:?}) was called when {x:?} is not in the alphabet");
    }

    pub fn build(seq: &[u8], bwt: Vec<u8>, sarray: Vec<u32>) -> Self {
        let mut alphabet = Vec::new();
        for x in seq {
            if *x != b'$' && !alphabet.contains(x) {
                alphabet.push(*x);
            }
        }
        alphabet.sort();

        let mut count = vec![0; alphabet.len()];
        let mut occ = Vec::with_capacity(alphabet.len() * (seq.len() + 1));
        occ.extend(&count);

        for &x in &bwt {
            if x != b'$' {
                let x_idx = Self::get_idx(&alphabet, x);
                count[x_idx] += 1;
            }

            occ.extend(&count);
        }
        assert_eq!(occ.len(), alphabet.len() * (seq.len() + 1));

        let mut counts = Vec::with_capacity(count.len());
        let mut sum = 1;
        for i in 0..count.len() {
            counts.push(sum);
            sum += count[i];
        }

        Self {
            bwt,
            occ,
            counts,
            alphabet,
            sarray,
        }
    }

    pub fn search(&self, query: &[u8]) -> Option<(u32, u32)> {
        let mut low = 0;
        let mut high = self.bwt.len() as u32;

        for &q in query.iter().rev() {
            let q_idx = Self::get_idx(&self.alphabet, q);
            low = self.counts[q_idx] + self.occ[(low as usize) * self.alphabet.len() + q_idx];
            high = self.counts[q_idx] + self.occ[(high as usize) * self.alphabet.len() + q_idx];

            if low >= high {
                return None;
            }
        }

        Some((low, high))
    }

    pub fn suffix_array(&self) -> &[u32] {
        &self.sarray
    }

    pub fn write(&self, out: &mut impl io::Write) -> io::Result<()> {
        let zero: u32 = 0;
        out.write(&zero.to_le_bytes())?;

        for count in &self.counts {
            out.write(&count.to_le_bytes())?;
        }
        for n in &self.occ {
            out.write(&n.to_le_bytes())?;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::FMIndex;

    fn banana_sequence() -> Vec<u8> {
        let mut seq = b"BANANA".to_vec();
        if !seq.ends_with(&[b'$']) {
            seq.push(b'$');
        }
        seq
    }

    fn build_banana_index() -> FMIndex {
        let seq = banana_sequence();
        let sa = crate::sarray::build(&seq);
        let bwt = crate::bwt::build(&seq, &sa);
        FMIndex::build(&seq, bwt, sa)
    }

    #[test]
    fn builds_alphabet_and_counts_for_banana() {
        let seq = banana_sequence();
        let sa = crate::sarray::build(&seq);
        let bwt = crate::bwt::build(&seq, &sa);
        let index = FMIndex::build(&seq, bwt, sa);

        assert_eq!(index.alphabet, vec![b'A', b'B', b'N']);
        assert_eq!(index.counts, vec![1, 4, 5]);
        assert_eq!(index.occ.len(), index.alphabet.len() * (seq.len() + 1));
        assert_eq!(index.suffix_array(), &[6, 5, 3, 1, 0, 4, 2]);
    }

    #[test]
    fn can_search_banana_for_ana() {
        let index = build_banana_index();
        assert_eq!(index.search(b"ANA"), Some((2, 4)));
        assert!(index.search(b"ABB").is_none());
    }
}
