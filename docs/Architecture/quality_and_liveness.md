# Face Quality Assessment & Liveness Detection Methodology

**Document Identifier:** `docs/Architecture/quality_and_liveness.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 1. Advanced Face Quality Assessment (FQA)

### 1.1 Methodology & Feature Attributes
The `QualityAssessor` module evaluates 6 distinct structural image quality factors:

1. **Blur / Sharpness ($S$):** Calculated via the Variance of Laplacian ($\sigma^2_{Lap} = \text{Var}(\Delta I)$). Normalized score:
   $$S = \min\left(1.0, \frac{\sigma^2_{Lap}}{250.0}\right)$$
2. **Brightness ($B$):** Measured via mean grayscale pixel intensity ($\mu_I$). Optimal target is mid-tone 128:
   $$B = \max\left(0.0, 1.0 - \frac{|\mu_I - 128.0|}{128.0}\right)$$
3. **Contrast ($C$):** Measured via grayscale standard deviation ($\sigma_I$):
   $$C = \min\left(1.0, \frac{\sigma_I}{64.0}\right)$$
4. **Resolution & Size ($R$):** Evaluated against bounding box area ($w \times h$) relative to standard $112 \times 112$ canonical crop:
   $$R = \min\left(1.0, \frac{w \cdot h}{112 \cdot 112}\right)$$
5. **Pose Rotation ($P$):** Estimated yaw ($\theta_{yaw}$) and pitch ($\theta_{pitch}$) from 5-point facial landmarks:
   $$P = \max\left(0.0, 1.0 - \max\left(\frac{|\theta_{yaw}|}{\theta_{max\_yaw}}, \frac{|\theta_{pitch}|}{\theta_{max\_pitch}}\right)\right)$$
6. **Symmetry & Occlusion ($O$):** Computed by measuring Mean Squared Error (MSE) between normalized left and right facial crop halves:
   $$O = \max\left(0.0, 1.0 - 4.0 \cdot \text{MSE}(I_{left}, I_{right\_flipped})\right)$$

### 1.2 Composite Quality Score $Q$
The composite normalized score $Q \in [0.0, 1.0]$ is computed as:
$$Q = w_S S + w_B B + w_C C + w_R R + w_P P + w_O O$$
where default weights are $\{0.30, 0.15, 0.15, 0.15, 0.15, 0.10\}$ summing to $1.0$.

---

## 2. Face Anti-Spoofing (FAS) Liveness Detection

### 2.1 Threat Model
The `LivenessDetector` module evaluates three primary presentation attack instruments (PAIs):
- **PAI-1: Printed Photograph Attack (2D Paper):** Static printed paper photos.
- **PAI-2: Digital Screen Replay Attack:** High-definition video replay on smartphones or tablets.
- **PAI-3: Static Mask / Photo Replay:** Non-moving facial photo presented to camera lens.

### 2.2 Anti-Spoofing Mechanisms
1. **2D Fast Fourier Transform (FFT) Power Spectrum Analysis:**
   Printed photos lose microscopic skin texture details in the high-frequency band. The high-frequency power ratio is computed across the shifted 2D magnitude spectrum.
2. **Specular Reflection & Moiré Pattern Glare Detection:**
   Digital screens introduce specular glass reflections and color saturation distortion. Saturation of value channel pixels ($V > 245$) flags screen replays (`SPOOF_SCREEN`).
3. **Multi-Frame Landmark Motion Dynamics:**
   Tracks nose tip landmark displacement variance across consecutive frames ($\sigma^2_{pos}$). Static presentation attacks produce near-zero variance ($\sigma^2_{pos} < 0.05$).

### 2.3 Output Classifications
- `LIVE`: Verified authentic human presence ($L_{composite} \ge 0.50$).
- `SPOOF_PRINT`: Flagged high-frequency texture attenuation (Paper photo attack).
- `SPOOF_SCREEN`: Flagged glass reflection glare or screen Moiré pattern.
- `FAILED_LIVENESS`: Composite liveness score below threshold.

---

## 3. SRS Traceability Matrix

- **`FR-008` (Face Quality Assessment):** Satisfied by `QualityAssessor` module.
- **`FR-009` (Face Liveness Detection):** Satisfied by `LivenessDetector` module.
- **`NFR-003` (Biometric Anti-Spoofing Robustness):** Verified via `test_quality_and_liveness.py`.
