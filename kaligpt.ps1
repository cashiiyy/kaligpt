param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

python -m agents @Arguments
