from CybORG.Shared.Config import CybORGConfig


if __name__ == "__main__":
    new_config = CybORGConfig.load_config(None)
    print(new_config)
