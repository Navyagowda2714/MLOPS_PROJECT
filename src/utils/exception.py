class PipelineError(Exception):
    """Raised when a pipeline stage cannot continue (bad data, model below threshold, ...)."""
