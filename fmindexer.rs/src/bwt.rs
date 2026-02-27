pub fn build(seq: &[u8], sarray: &[u32]) -> Vec<u8> {
    let mut bwt = Vec::with_capacity(seq.len());

    for i in 0..seq.len() {
        if sarray[i] == 0 {
            bwt.push(b'$');
        } else {
            bwt.push(seq[sarray[i] as usize - 1]);
        }
    }

    bwt
}

#[cfg(test)]
mod tests {
    use super::build;

    fn banana_sequence() -> Vec<u8> {
        let mut seq = b"BANANA".to_vec();
        if !seq.ends_with(&[b'$']) {
            seq.push(b'$');
        }
        seq
    }

    #[test]
    fn builds_bwt_for_banana() {
        let seq = banana_sequence();
        let sa = crate::sarray::build(&seq);
        let bwt = build(&seq, &sa);
        assert_eq!(bwt, b"ANNB$AA");
    }
}
