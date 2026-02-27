mod bwt;
mod fm_index;
mod sarray;

use fm_index::FMIndex;
use serde_json::json;
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, Read};
use std::path::Path;

fn build_index(seq: &[u8], save: &Path) {
    let suffix_array = sarray::build(seq);
    let bwt = bwt::build(seq, &suffix_array);
    let index = FMIndex::build(seq, bwt, suffix_array);

    let bytes = postcard::to_stdvec(&index).unwrap();
    std::fs::write(save, bytes).unwrap();
}

fn search(index_path: &Path, query: &[u8]) {
    let start = std::time::Instant::now();
    let bytes = fs::read(index_path).unwrap();
    let index: FMIndex = postcard::from_bytes(&bytes).unwrap();
    eprintln!("Loaded index in {:.2?}", start.elapsed());

    let start = std::time::Instant::now();
    if let Some((low, high)) = index.search(query) {
        for i in (low..high).rev() {
            println!("{}", index.suffix_array()[i as usize]);
        }
    } else {
        eprintln!("No results");
    }
    eprintln!("Search completed in {:.2?}", start.elapsed());
}

fn load_index(index_path: &Path) -> FMIndex {
    let bytes = fs::read(index_path).unwrap();
    postcard::from_bytes(&bytes).unwrap()
}

fn search_many(index_path: &Path, queries_path: &Path) {
    let index = load_index(index_path);
    let suffix_array = index.suffix_array();
    let file = File::open(queries_path).unwrap();
    let reader = BufReader::new(file);

    for line in reader.lines() {
        let query = line.unwrap_or_default();
        let positions: Vec<u32> = if query.is_empty() {
            Vec::new()
        } else {
            index
                .search(query.as_bytes())
                .map(|(low, high)| (low..high).map(|i| suffix_array[i as usize]).collect())
                .unwrap_or_else(Vec::new)
        };
        println!(
            "{}",
            serde_json::to_string(&json!({"query": query, "positions": positions})).unwrap()
        );
    }
}

fn main() {
    let app = clap::Command::new("fmindex")
        .subcommand_required(true)
        .subcommand(
            clap::Command::new("build")
                .arg(clap::arg!(<input> "Input sequence file").required(true))
                .arg(clap::arg!(<output> "Output index file").required(true)),
        )
        .subcommand(
            clap::Command::new("search")
                .arg(clap::arg!(<index> "Input index file").required(true))
                .arg(clap::arg!(<query> "Query string").required(true)),
        )
        .subcommand(
            clap::Command::new("search-many")
                .arg(clap::arg!(<index> "Input index file").required(true))
                .arg(clap::arg!(<queries> "Newline-delimited queries file").required(true)),
        );

    let matches = app.get_matches();

    match matches.subcommand().unwrap() {
        ("build", matches) => {
            let input = matches.get_one::<String>("input").unwrap();
            let output = matches.get_one::<String>("output").unwrap();

            let mut file = io::BufReader::new(File::open(input).unwrap());
            let mut seq = Vec::new();
            file.read_to_end(&mut seq).unwrap();
            if !seq.ends_with(&[b'$']) {
                seq.push(b'$');
            }

            build_index(&seq, Path::new(output));
        }
        ("search", matches) => {
            let index = matches.get_one::<String>("index").unwrap();
            let query = matches.get_one::<String>("query").unwrap();

            search(Path::new(index), query.as_bytes());
        }
        ("search-many", matches) => {
            let index = matches.get_one::<String>("index").unwrap();
            let queries = matches.get_one::<String>("queries").unwrap();

            search_many(Path::new(index), Path::new(queries));
        }
        _ => unreachable!(),
    }
}
