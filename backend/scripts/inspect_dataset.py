from expense_analyzer.ml.datasets.loader import DatasetLoader
from expense_analyzer.ml.datasets.inspector import DatasetInspector


def main() -> None:
    loader = DatasetLoader()
    inspector = DatasetInspector()

    dataframe = loader.load()
    statistics = inspector.inspect(dataframe)

    print("\nDataset")
    print("-------")
    print(f"Rows: {statistics.row_count:,}")
    print(f"Columns: {statistics.column_count}")

    print("\nColumns")
    print("-------")
    for column, data_type in statistics.columns.items():
        print(f"{column:<15} {data_type}")

    print("\nMissing values")
    print("--------------")
    for column, values in statistics.missing_values.items():
        print(
            f"{column:<15} "
            f"{values.missing_count:>5} "
            f"({values.missing_percentage:.2f}%)"
        )

    print("\nCategories")
    print("----------")
    for category, values in statistics.category_distribution.items():
        print(
            f"{category:<20} "
            f"{values.record_count:>5} "
            f"({values.percentage:.2f}%)"
        )

    print("\nDuplicates")
    print("----------")
    print(f"Duplicate records: {statistics.duplicate_count}")

    print("\nAmount statistics")
    print("-----------------")
    print(f"Min:  {statistics.amount_statistics.min:,.2f}")
    print(f"Max:  {statistics.amount_statistics.max:,.2f}")
    print(f"Mean: {statistics.amount_statistics.mean:,.2f}")


if __name__ == "__main__":
    main()