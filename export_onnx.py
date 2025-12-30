import os
import subprocess
import sys

def main():
    model_name = "cointegrated/rubert-tiny2"
    output_dir = "models/onnx_model"
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Экспорт модели {model_name} в ONNX формат...")
    print("Это может занять некоторое время...")
    
    print("Шаг 1: Экспорт в ONNX...")
    cmd_export = [
        sys.executable, "-m", "optimum.cli.export",
        "onnx",
        "--model", model_name,
        "--task", "feature-extraction",
        output_dir
    ]
    
    try:
        subprocess.run(cmd_export, check=True)
        print("Экспорт завершен!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при экспорте: {e}")
        sys.exit(1)
    
    print("Шаг 2: Квантование модели...")
    try:
        from optimum.onnxruntime import ORTQuantizer
        from optimum.onnxruntime.configuration import QuantizationConfig
        from optimum.onnxruntime import ORTModelForFeatureExtraction
        
        model = ORTModelForFeatureExtraction.from_pretrained(output_dir)
        quantizer = ORTQuantizer.from_pretrained(model)
        
        quantization_config = QuantizationConfig(
            is_static=True,
            format="QOperator",
            mode="IntegerOps",
            activations_dtype="QInt8",
            weights_dtype="QInt8"
        )
        
        quantizer.quantize(
            quantization_config=quantization_config,
            save_dir=output_dir
        )
        print("Квантование завершено!")
        print(f"Модель сохранена в {output_dir}")
    except Exception as e:
        print(f"Предупреждение: не удалось выполнить квантование: {e}")
        print("Модель экспортирована без квантования")
        print(f"Модель сохранена в {output_dir}")

if __name__ == "__main__":
    main()

