from dataclasses import dataclass
from src.cleaner import clean_dataframe
from pipeline.validate import validate_dataset, quality_score

@dataclass
class ETLResult:
    raw_rows: int
    clean_rows: int
    removed_rows: int
    checks: list
    quality_score: int
    actions: list
    status: str = "SUCCESS"

def run_etl(df, mapping):
    checks = validate_dataset(df, mapping)
    cleaned, actions = clean_dataframe(df)
    score = quality_score(checks, cleaned)
    result = ETLResult(
        raw_rows=len(df),
        clean_rows=len(cleaned),
        removed_rows=len(df) - len(cleaned),
        checks=checks,
        quality_score=score,
        actions=actions
    )
    return result, cleaned
