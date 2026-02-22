#!/usr/bin/env python3
import random
import argparse


def generate(length):
    alphabet = ['A', 'C', 'T', 'G']
    return ''.join(random.choice(alphabet) for _ in range(length))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('length', type=int, help='Length of sequence to generate')

    args = parser.parse_args()

    print(generate(args.length))
