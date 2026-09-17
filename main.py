from edesur import extract_transform_edesur
from dgii import extract_transform_dgii
from load import load_edesur, load_dgii


def main():

    # EDESUR
    df_edesur = extract_transform_edesur()
    load_edesur(df_edesur)

    # DGII
    df_dgii = extract_transform_dgii()
    load_dgii(df_dgii)


if __name__ == "__main__":
    main()