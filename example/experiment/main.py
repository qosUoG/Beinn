def main():
    print("Hello from experiment!")


if __name__ == "__main__":
    import examplelib.ExampleDriver

    print(getattr(examplelib.ExampleDriver.ExampleEquipment, "equipment_params"))
