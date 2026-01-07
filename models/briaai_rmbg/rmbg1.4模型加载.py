from transformers import AutoModelForImageSegmentation

model = AutoModelForImageSegmentation.from_pretrained("briaai/RMBG-1.4", trust_remote_code=True)
model.save_pretrained("./models/briaai_rmbg")
