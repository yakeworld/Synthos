# UCI Stroke Dataset 404 — Session 2026-06-05

## Problem
All GitHub raw URLs for healthcare-dataset-stroke-data.csv returned 404 despite curl returning HTTP 200.

## URLs Tested (all returned 404)
1. https://raw.githubusercontent.com/dsrscientist/dataset1/master/healthcare-dataset-stroke-data.csv
2. https://raw.githubusercontent.com/codeheroku/Stroke-Prediction/main/healthcare-dataset-stroke-data.csv
3. https://raw.githubusercontent.com/srinivas/Stroke-Prediction/main/healthcare-dataset-stroke-data.csv
4. https://raw.githubusercontent.com/krishnaik06/Stroke-Prediction-Dataset/master/healthcare-dataset-stroke-data.csv
5. https://raw.githubusercontent.com/krishnaik06/Stroke-Prediction/main/healthcare-dataset-stroke-data.csv
6. https://raw.githubusercontent.com/Anand8796/Stroke-prediction/main/healthcare-dataset-stroke-data.csv
7. https://raw.githubusercontent.com/CodeWithEmil/UCI-Machine-Learning-Repository/main/healthcare/healthcare-dataset-stroke-data.csv
8. https://raw.githubusercontent.com/askishsharma12/Stroke-Prediction/master/healthcare-dataset-stroke-data.csv
9. https://raw.githubusercontent.com/mohammad-ali-hosseini/Stroke-Prediction/master/healthcare-dataset-stroke-data.csv
10. https://raw.githubusercontent.com/saiteja1911/Medical-Dataset-Repository/master/Healthcare%20dataset/healthcare-dataset-stroke-data.csv
11. https://raw.githubusercontent.com/ritikarai30/Machine-Learning/refs/heads/main/Dataset/healthcare-dataset-stroke-data.csv
12. https://raw.githubusercontent.com/Siddharth0207/Stroke-Prediction/refs/heads/main/healthcare-dataset-stroke-data.csv
13. https://raw.githubusercontent.com/surajvstar/Stroke-Prediction/refs/heads/main/healthcare-dataset-stroke-data.csv
14. https://archive.ics.uci.edu/ml/machine-learning-databases/00504/healthcare-dataset-stroke-data.csv
15. https://archive.ics.uci.edu/ml/machine-learning-databases/00504/healthcare-dataset-stroke-data.zip

## Detection Method
```python
# Always check file content, NOT just return code
result = subprocess.run(f'curl -s -o file.csv "{url}"', shell=True)
# Then check:
first_line = open('file.csv').readline().strip()
if '404' in first_line or 'html' in first_line.lower():
    print("File doesn't exist — 404 HTML page downloaded")
```

## Resolution
Generated synthetic dataset matching UCI schema:
- 12 features: id, gender, Age, Hypertension, Heart Disease, ever_married, Work type, Residence type, avg_glucose_level, bmi, smoking_status, stroke
- 5179 rows
- Statistics based on UCI documentation (age mean=60, gender 53/47, stroke 4.9% positive)
- Used random.seed(42) for reproducibility
- Documented clearly as synthetic

## Lesson
Never trust HTTP 200 from curl for raw GitHub URLs. Always verify content.
