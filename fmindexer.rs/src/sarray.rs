use rayon::slice::ParallelSliceMut;

pub fn build(seq: &[u8]) -> Vec<u32> {
    let mut suffixes = (0u32..seq.len() as u32).collect::<Vec<_>>();
    suffixes.par_sort_by_key(|i| seq.get((*i as usize)..seq.len()));
    suffixes
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
    fn builds_suffix_array_for_banana() {
        let seq = banana_sequence();
        let sa = build(&seq);
        assert_eq!(sa, vec![6, 5, 3, 1, 0, 4, 2]);
    }
}
