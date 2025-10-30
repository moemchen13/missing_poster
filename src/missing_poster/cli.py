# poster_tools/cli.py
import argparse
from missing_poster.create_csv import create_csv
from missing_poster.csv_to_missing_poster import csv_to_posters, read_csv

def main():
    parser = argparse.ArgumentParser(prog="missing_poster", description="Missing Poster Tools CLI")
    subparsers = parser.add_subparsers(dest="command")

    # create_csv command
    parser_csv = subparsers.add_parser("create_csv", help="Create a CSV from directory with pictures")
    parser_csv.add_argument("-i","--input_dir", help="Directory with images named after persons",type=str,required=True)
    parser_csv.add_argument("-o","--output_dir", help="Path to output of csv",type=str,default="out")
    parser_csv.add_argument("-f","--output_filename", help="csv filename",type=str,default="missing_poster.csv")
    parser_csv.add_argument("-s","--seed",help="Seed for reproducibility",default=42,type=int)
    parser_csv.add_argument("-na","--n_attributes",help="number of attributes in the csv",default=3,type=int)
    

    # from_csv_create_missing_posters command
    parser_missing = subparsers.add_parser("csv_to_missing_posters", help="Create missing posters from a CSV")
    parser_missing.add_argument("-csv","--csv_path", help="Path to CSV file",type=str,required=True)
    parser_missing.add_argument("-o","--output_dir", help="Output directory for missing posters",type=str,default="out")
    parser_missing.add_argument("-n","--numbers",help="Phone numbers to choose from on poster",nargs="+",type=str,default=["017621663536", "01629567590"])

    args = parser.parse_args()
    
    if args.command == "create_csv":
        create_csv(args.input_dir,args.output_filename, args.output_dir,n_attributes=args.n_attributes,seed=args.seed)
    elif args.command == "csv_to_missing_posters":
        missing_person_df = read_csv(args.csv_path)
        print(args.numbers[0])
        csv_to_posters(missing_person_df, args.output_dir,phone_numbers=args.numbers)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
