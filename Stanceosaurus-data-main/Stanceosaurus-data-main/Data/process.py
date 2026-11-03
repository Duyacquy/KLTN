import pandas as pd
import argparse
from emoji import demojize
from nltk.tokenize import TweetTokenizer

def read_english(data_file):
    df = pd.read_excel(data_file)
    df.columns = ['number', 'date', 'status id', 'in reply to id', 'username', 'meta_info', 
                            'claim', 'text', 'context', 'title', 'final_annotation', 'final_leaning', 'note_3']
    df.reset_index(inplace=True)
    df = df.fillna('')
    return df

def read_arabic(data_file):
    df = pd.read_excel(data_file)
    df.columns = ['number', 'claim', 'status id', 'in reply to id', 'username', 'text', 'context',
                            'final_annotation', 'final_leaning']
    
    df['date'] = ''
    df['meta_info'] = ''
    df['title'] = ''
    df['note_3'] = ''
    
    df = df[['number', 'date', 'status id', 'in reply to id', 'username', 'meta_info', 
                            'claim', 'text', 'context', 'title', 'final_annotation', 'final_leaning', 'note_3']]

    df.reset_index(inplace=True)
    df = df.fillna('')
    return df

def read_hindi(data_file):
    df = pd.read_excel(data_file)
    df.columns = ['number', 'date', 'status id', 'in reply to id', 'meta_info', 'username',
                            'claim', 'text', 'context', 'title', 'final_annotation', 'final_leaning']

    df['note_3'] = ''

    df = df[['number', 'date', 'status id', 'in reply to id', 'meta_info', 'username', 
                            'claim', 'text', 'context', 'title', 'final_annotation', 'final_leaning', 'note_3']]

    df.reset_index(inplace=True)
    df = df.fillna('')
    return df

def normalizeToken(token, username_token, url_token, separation_token):
    lowercased_token = token.lower()
    if token.startswith("@"):
        return username_token
    elif lowercased_token.startswith("http") or lowercased_token.startswith("www"):
        return url_token
    elif len(token) == 1:
        return demojize(token)
    else:
        if token == "’":
            return "'"
        elif token == "…":
            return "..."
        else:
            return token

def normalizeTweet(tweet, username_token, url_token, separation_token):
    tokenizer = TweetTokenizer()
    tokens = tokenizer.tokenize(tweet.replace("’", "'").replace("…", "..."))
    normTweet = " ".join([normalizeToken(token, username_token, url_token, separation_token) for token in tokens])

    normTweet = (
        normTweet.replace("cannot ", "can not ")
        .replace("n't ", " n't ")
        .replace("n 't ", " n't ")
        .replace("ca n't", "can't")
        .replace("ai n't", "ain't")
    )
    normTweet = (
        normTweet.replace("'m ", " 'm ")
        .replace("'re ", " 're ")
        .replace("'s ", " 's ")
        .replace("'ll ", " 'll ")
        .replace("'d ", " 'd ")
        .replace("'ve ", " 've ")
    )
    normTweet = (
        normTweet.replace(" p . m .", "  p.m.")
        .replace(" p . m ", " p.m ")
        .replace(" a . m .", " a.m.")
        .replace(" a . m ", " a.m ")
    )
    a = " ".join(normTweet.split())
    if separation_token == "[SEP]":
        return a.replace("[ SEP ]", "[SEP]")
    return a

def normalize(df, username_token, url_token, separation_token):
    for (i, row) in df.iterrows():
        x = row["final text"]
        if not pd.isna(x):
            a = normalizeTweet(x, username_token, url_token, separation_token)
            df.at[i, "final text"] = a

        b = row["claim"]
        if not pd.isna(b):
            c = normalizeTweet(b, username_token, url_token, separation_token)
            df.at[i, "claim"] = c
    
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file", default=None, type=str, required=True,
                        help="The data file to process.")
    parser.add_argument("--normalize", default=True, type=bool, required=True,
                        help="Normalize data or not.")
    parser.add_argument("--number_labels", default=5, choices=[3, 5], type=int, required=True,
                        help="5 or 3 class stance identification.")
    parser.add_argument("--username_replacement", default="@USER", type=str, required=False,
                        help="Token to replace Usernames.")
    parser.add_argument("--website_replacement", default="HTTPURL", type=str, required=False,
                        help="Token to replace URLs.")
    parser.add_argument("--separation_token", default="[SEP]", type=str, required=False,
                        help="Token to separate texts.")
    parser.add_argument("--language", choices=['english', 'hindi', 'arabic'], default='english', type=str, required=False,
                        help="If the language is English.")

    args = parser.parse_args()

    if args.language == 'english':
        df = read_english(args.data_file)
    if args.language == 'arabic':
        df = read_arabic(args.data_file)
    if args.language == 'hindi':
        df = read_hindi(args.data_file)

    df['final text'] = df[['text', 'context']].agg(' [SEP] '.join, axis=1)
    col = df.columns
    lst = []
    for i, row in df.iterrows():
        if row['final text'][-7:] == " [SEP] ":
            row['final text'] = row['final text'][:-7]
        lst.append(row)
    df = pd.DataFrame(lst, columns=col)
    df['final text'] = df[['final text', 'title']].agg(' [SEP] '.join, axis=1)

    col = df.columns
    lst = []
    for i, row in df.iterrows():
        if row['final text'][-7:] == " [SEP] ":
            row['final text'] = row['final text'][:-7]
        lst.append(row)
    df = pd.DataFrame(lst, columns=col)

    df['text'] = df['text'].str.replace('\n', ' ')
    df['context'] = df['context'].str.replace('\n', ' ')
    df['final text'] = df['final text'].str.replace('\n', ' ')
    df['title'] = df['title'].str.replace('\n', ' ')
    df['final_annotation'] = df['final_annotation'].str.strip()
    df['final_leaning'] = df['final_leaning'].str.strip()
    if args.number_labels == 3:
        df['stance'] = df['final_annotation'] + " " + df['final_leaning']
        df['stance'] = df['stance'].str.strip()
        df.loc[df["stance"] == "Supporting", "stance"] = "Supporting"
        df.loc[df["stance"] == "Irrelevant", "stance"] = "Other"
        df.loc[(df["stance"] == "Discussing Supporting"),"stance"] = "Supporting"
        df.loc[(df["stance"] == "Discussing Refuting"),"stance"] = "Refuting"
        df.loc[(df["stance"] == "Discussing Neutral"), "stance"] = "Other"
        df.loc[(df["stance"] == "Discussing"), "stance"] = "Other"
        df.loc[df["stance"] == "Querying", "stance"] = "Other"
        df.loc[df["stance"] == "Refuting", "stance"] = "Refuting"
    else:
        df['stance'] = df['final_annotation']
    
    if args.normalize:
        df = normalize(df, args.username_replacement, args.website_replacement, args.separation_token)

    # print(df.head())
    # print(df.shape)
    df.to_csv((args.data_file[:-5] + "_" + str(args.number_labels)).lower() + "_class.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
