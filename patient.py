import random
import dataclasses
from dataclasses import dataclass, fields, field
import os 
import json
import streamlit as st

PATIENT_DATA_FILE = "patient_data.json"

# this is new comment.

# The average body temperature is 98.6 F (37 C). But normal body temperature can range between 97 F (36.1 C) and 99 F (37.2 C)

# ideal blood pressure is considered to be between 90/60mmHg and 120/80mmHg. high blood pressure is considered to be 140/90mmHg or higher. low blood pressure is considered to be below 90/60mmHg

# A normal resting heart rate for adults ranges from 60 to 100 beats per minute.

# The normal respiratory rate for healthy adults is between 12–20 breaths per minute

# The expected values for normal fasting blood glucose concentration are between 70 mg/dL (3.9 mmol/L) and 100 mg/dL (5.6 mmol/L).

# normal pulse oximeter reading for your oxygen saturation level is between 95% and 100%.

class IdealRange:
    body_temperature_celcius = slice(36.1, 37.3)
    blood_pressure_systolic_mm_hg = slice(90, 121)
    blood_pressure_diastolic_mm_hg = slice(60, 81)
    resting_heart_rate_bpm = slice(60, 101)
    respiratory_rate_bpm = slice(12, 21)
    blood_glucose_mg_dL = slice(70, 101)
    blood_saturation = slice(95, 100)
    sodium_rate = slice(135, 145)  # Normal range: 135-145 mEq/L
    potassium_rate = slice(3.5, 5.1)  # Normal range: 3.5-5.1 mEq/L


class AllowedRange:
    body_temperature_celcius = slice(30, 40)
    blood_pressure_systolic_mm_hg = slice(20, 300)
    blood_pressure_diastolic_mm_hg = slice(20, 300)
    resting_heart_rate_bpm = slice(0, 220)
    respiratory_rate_bpm = slice(0, 60)
    blood_glucose_mg_dL = slice(0, 350)
    blood_saturation = slice(0, 100)
    sodium_rate = slice(120, 160)  # Extended range
    potassium_rate = slice(2.5, 6.5)  # Extended range

@dataclass
class Patient:
    body_temperature_celcius: float = field(default=None)
    blood_pressure_systolic_mm_hg: int = field(default=None)
    blood_pressure_diastolic_mm_hg: int = field(default=None)
    resting_heart_rate_bpm: int = field(default=None)
    respiratory_rate_bpm: int = field(default=None)
    blood_glucose_mg_dL: float = field(default=None)
    blood_saturation: int = field(default=None)
    sodium_rate: float = field(default=None)
    potassium_rate: float = field(default=None)

    def __post_init__(self):
        """Initialize with ideal values if None is set."""
        for field in fields(self):
            if getattr(self, field.name) is None:
                sl = getattr(IdealRange, field.name)
                val = random.uniform(sl.start, sl.stop)
                setattr(self, field.name, round(val, 2))

    def to_dict(self):
        """Convert the Patient object to a dictionary."""
        return {
            "body_temperature_celcius": self.body_temperature_celcius,
            "blood_pressure_systolic_mm_hg": self.blood_pressure_systolic_mm_hg,
            "blood_pressure_diastolic_mm_hg": self.blood_pressure_diastolic_mm_hg,
            "resting_heart_rate_bpm": self.resting_heart_rate_bpm,
            "respiratory_rate_bpm": self.respiratory_rate_bpm,
            "blood_glucose_mg_dL": self.blood_glucose_mg_dL,
            "blood_saturation": self.blood_saturation,
            "sodium_rate": self.sodium_rate,
            "potassium_rate": self.potassium_rate
        }

    def _gte_or_lt(self, f):
        self_value = getattr(self, f)
        max_allowed = getattr(IdealRange, f).stop
        min_allowed = getattr(IdealRange, f).start
        return (self_value < min_allowed) or (self_value >= max_allowed)

    def _gte(self, f):
        self_value = getattr(self, f)
        max_allowed = getattr(IdealRange, f).stop
        return self_value >= max_allowed

    def _lt(self, f):
        self_value = getattr(self, f)
        min_allowed = getattr(IdealRange, f).start
        return self_value < min_allowed

    def _normal_or_gte(self, f):
        self_value = getattr(self, f)
        min_allowed = getattr(IdealRange, f).start
        return self_value >= min_allowed

    def _normal_or_lt(self, f):
        self_value = getattr(self, f)
        max_allowed = getattr(IdealRange, f).stop
        return self_value < max_allowed

    @staticmethod
    def load_patient_data():
        """Load patient data from a JSON file and normalize the keys."""
        if os.path.exists(PATIENT_DATA_FILE):
            with open(PATIENT_DATA_FILE, "r") as file:
                try:
                    data = json.load(file)

                    # Mapping from JSON keys to Patient class attributes
                    normalized_data = {
                        "body_temperature_celcius": data.get("temperature", {}).get("value", 36.8),
                        "blood_pressure_systolic_mm_hg": data.get("bp_systolic", data.get("blood_pressure", {}).get("value", 120)),
                        "blood_pressure_diastolic_mm_hg": data.get("bp_diastolic", data.get("blood_pressure_diastolic_mm_hg", 80)),
                        "resting_heart_rate_bpm": data.get("heart_rate", 75),
                        "respiratory_rate_bpm": data.get("respiratory_rate", 16),
                        "blood_glucose_mg_dL": data.get("blood_glucose", data.get("glucose", {}).get("value", 90)),
                        "blood_saturation": data.get("blood_saturation", data.get("saturation", {}).get("value", 98)),
                        "sodium_rate": data.get("sodium_rate", 140),
                        "potassium_rate": data.get("potassium_rate", 4.2)
                    }
                    
                    return normalized_data
                except json.JSONDecodeError:
                    print("Error: JSON file is empty or corrupted. Initializing new data.")
        
        # Return a new patient object as a dictionary if file is missing or invalid
        return Patient().to_dict()


    @staticmethod
    def save_patient_data(data):
        """Save patient data to a JSON file."""
        with open(PATIENT_DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)


def render_metrics(p: Patient):
    stats_map = {
        'Blood Pressure': 'blood_pressure_systolic_mm_hg',
        'Body temperature': 'body_temperature_celcius',
        'Blood saturation': 'blood_saturation',
        'Blood glucose': 'blood_glucose_mg_dL',
        'Heart rate': 'resting_heart_rate_bpm'
    }

    cols_stats = st.columns(len(stats_map))
    for col, (stat_label, stat_attr) in zip(cols_stats, stats_map.items()):
        with col:
            p_value = getattr(p, stat_attr)
            min_value = getattr(IdealRange, stat_attr).start
            max_value = getattr(IdealRange, stat_attr).stop

            if min_value < p_value < max_value:
                delta = 0
            elif p_value < min_value:
                delta = p_value - min_value
            else:
                delta = p_value - max_value
            st.metric(label=stat_label, value=p_value, delta=f"{delta:.2f}")


DISEASES = []


def disease(fn):
    DISEASES.append(fn)


@disease
def penumonia(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Pneumonia"


@disease
def pulmonary_embolism(p: Patient):
    if all((
            p._lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Pulmonary Embolism"


@disease
def COPD(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Pulmonary Embolism"


@disease
def asthma_exacerbation(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Asthma Exacerbation"


@disease
def ARDS(p: Patient):
    if all((
            p._lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "ARDS"


@disease
def pulmonary_edema(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Pulmonary Edema"


@disease
def bronchiolitis(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Bronchiolitis"


@disease
def pleural_effusion(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Pleural Effusion"


@disease
def CHF(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte_or_lt('resting_heart_rate_bpm')
    )):
        return "CHF"


@disease
def pulmonary_fibrosis(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Pulmonary Fibrosis"


@disease
def lung_cancer(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte_or_lt('resting_heart_rate_bpm')
    )):
        return "Lung Cancer"


@disease
def acute_bronchitis(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Acute Bronchitis"


@disease
def tuberculosis(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Tuberculosis (TB)"


@disease
def cystic_fibrosis(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Cystic Fibrosis"


@disease
def pneumothorax(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Pneumothorax"


@disease
def interstitial_lung_disease(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Interstitial Lung Disease"


@disease
def pulmonary_hypertension(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte_or_lt('resting_heart_rate_bpm')
    )):
        return "Pulmonary Hypertension"


@disease
def sepsis(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Sepsis"


@disease
def diabetic_ketoacidosis(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Diabetic Ketoacidosis (DKA)"


@disease
def metabolic_acidosis(p: Patient):
    if all((
            p._lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._normal_or_gte('blood_saturation'),
            p._lt('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Metabolic Acidosis"


@disease
def heatstroke(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Heatstroke"


@disease
def anemia(p: Patient):
    if all((
            p._lt('blood_pressure_systolic_mm_hg'),
            p._lt('body_temperature_celcius'),
            p._normal_or_lt('blood_saturation'),
            p._normal_or_lt('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Anemia"


@disease
def thyroid_storm(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._normal_or_lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Thryoid Storm"


@disease
def drug_overdose(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte_or_lt('resting_heart_rate_bpm')
    )):
        return "Drug Overdose"


@disease
def Anxiety_or_Panic_Attacks(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte_or_lt('resting_heart_rate_bpm')
    )):
        return "Anxiety or Panic Attacks"


@disease
def neurological_disorders(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._normal_or_lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte_or_lt('resting_heart_rate_bpm')
    )):
        return "Neurological Disorders"


@disease
def acidosis(p: Patient):
    if all((
            p._lt('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._normal_or_lt('blood_saturation'),
            p._lt('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Acidosis (Respiratory or Metabolic)"


@disease
def sarcoidosis(p: Patient):
    if all((
            p._normal_or_gte('blood_pressure_systolic_mm_hg'),
            p._gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte('resting_heart_rate_bpm')
    )):
        return "Sarcoidosis"


@disease
def myasthenia_gravis(p: Patient):
    if all((
            p._lt('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._normal_or_lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._lt('resting_heart_rate_bpm')
    )):
        return "Myasthenia Gravis"


@disease
def sleep_apnea_exacerbation(p: Patient):
    if all((
            p._gte_or_lt('blood_pressure_systolic_mm_hg'),
            p._normal_or_gte('body_temperature_celcius'),
            p._lt('blood_saturation'),
            p._normal_or_gte('blood_glucose_mg_dL'),
            p._gte_or_lt('resting_heart_rate_bpm')
    )):
        return "Sleep Apnea Exacerbation"


p = Patient()