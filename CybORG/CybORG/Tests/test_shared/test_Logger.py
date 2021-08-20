from CybORG.Shared.Logger import CybORGLogger, log_trace
from CybORG.Shared.Config import CybORGConfig


@log_trace
def logger_test_func(msg):
    CybORGLogger.info(f"Test of log_trace decorator - {msg}")


if __name__ == "__main__":
    config = CybORGConfig.load_config()
    CybORGLogger.setup(config)

    CybORGLogger.debug("This is a debug message")
    CybORGLogger.info("This is an info message")
    CybORGLogger.warning("This is a warning message")
    CybORGLogger.error("This is an error message")
    CybORGLogger.critical("This is a critical message")
    CybORGLogger.header("I'm a header")

    logger_test_func("Testing decorator")
