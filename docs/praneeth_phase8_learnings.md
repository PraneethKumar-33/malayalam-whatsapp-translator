# Phase 8 Progress & Learnings: IndicLID Runtime Patch
**Author:** Praneeth Kumar (@PraneethKumar-33)

## 🎯 What was the task?
The goal of Phase 8 was to reproduce the original AI4Bharat IndicLID inference runtime in Google Colab so that it could be ported into the FastAPI backend. However, the legacy model was crashing on load, causing a "runtime/frontend failure" that blocked the project.

## 🚀 What I Accomplished
I successfully debugged and patched the legacy AI model to run flawlessly on modern environments. 

1. **Reproducible Environment**: Built a clean Colab setup that pins the exact AI4Bharat commit (`e4bfe42923...`) and safely downloads the fastText/BERT checkpoints.
2. **Root Cause Analysis**: Discovered that the original AI4Bharat `.pt` file was saved using Python's `pickle` on the entire object structure (instead of just weights). When modern `transformers` loaded it, it crashed because the old 2023 `BertConfig` and `BertAttention` objects were missing modern attributes (like `_attn_implementation_internal` and `token_type_ids`).
3. **The Ultimate Runtime Upgrade Patch**: Instead of downgrading Python libraries, I built a runtime patch that:
   - Extracts the raw weights (`state_dict`) from the broken legacy model.
   - Generates a brand new, modern `BertForSequenceClassification` object.
   - Safely injects the weights using `strict=False` while verifying that only obsolete buffers (like `position_ids`) are discarded.
4. **Pipeline Verification**: Wrote full-pipeline smoke tests using `batch_predict` to prove that Native Malayalam, Roman Malayalam, and English route perfectly to their respective models (`IndicLID-FTN`, `IndicLID-FTR`, and `IndicLID-BERT`).

## 🧠 What I Learned
- **Deep Learning Model Serialization:** I learned why saving models as entire objects (`torch.save(model)`) is dangerous and brittle, and why saving just the weights (`state_dict`) is the industry standard.
- **Model Upgrades:** I learned how to "transplant" the brain (weights) of an old AI model into a fresh, modern architectural body to fix library incompatibility crashes.
- **PyTorch strict loading:** I learned how to handle PyTorch's `strict=False` flag to safely ignore outdated legacy buffers.
- **Advanced Git Workflow:** I leveled up my terminal skills by managing SSH keys, copying files between directories, and pushing commits directly to a teammate's Pull Request branch.

With these patches verified, Nikhith is now fully unblocked to integrate this into the FastAPI backend!
