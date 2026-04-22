from argparse import ArgumentParser

from tempfile import TemporaryDirectory

def main():
    p = ArgumentParser(description="A utility to evaluate a architecture.")
    p.add_argument("--template", help="Path to the platform template to evaluate")

    args = p.parse_args()
    
    with TemporaryDirectory() as d:
        print(d)
    
if __name__ == "__main":
    main()
