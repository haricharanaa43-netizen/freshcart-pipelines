from sklearn.model_selection import train_test_split


def transform(df):
    out = df.copy()

    train_idx, test_idx = train_test_split(
        df.index,
        test_size=0.3,
        random_state=42,
        stratify=df["target"]
    )

    out["split"] = "train"
    out.loc[test_idx, "split"] = "test"

    return out