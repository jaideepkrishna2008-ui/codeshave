from tokenskel.estimator import compute_savings, estimate_tokens


def test_estimate_tokens():
    text = "def hello():\n    return 'world'"
    tokens = estimate_tokens(text)
    assert tokens > 0


def test_compute_savings():
    original = "def heavy_computation():\n" + "    x = 1\n" * 100 + "    return x"
    compressed = "def heavy_computation():\n    ..."
    report = compute_savings(original, compressed)

    assert report.original_tokens > report.compressed_tokens
    assert report.reduction_percentage > 50.0
    assert report.tokens_saved > 0
