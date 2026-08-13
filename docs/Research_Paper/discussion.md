# Chapter 6: Scientific Discussion & Critical Analysis

**Document Identifier:** `docs/Research_Paper/discussion.md`  
**Version:** 1.0.0  
**Date:** August 2026  
**Author:** Lead Software Architect & Research Engineer  

---

## 6.1 Scientific Interpretation of Results

The empirical results presented in Chapter 5 demonstrate a statistically meaningful improvement in system robustness and security when employing the **Quality-Aware Multi-Factor Confidence Scoring (QMF-Score)** engine compared to conventional fixed-threshold systems.

### 6.1.1 Statistically Meaningful Improvements
1. **Zero False Attendance Rate ($FAR_{attn} = 0.0\%$):** The Baseline system exhibited a $37.5\%$ false acceptance rate under presentation attack scenarios (2D paper prints and smartphone video replays), as cosine similarity alone cannot differentiate physical skin texture from printed ink or screen pixels. The Proposed QMF system achieved a **$100.0\%$ rejection rate** for presentation attacks via high-frequency FFT power spectrum analysis and specular reflection detection.
2. **Illumination Adaptation:** Under non-ideal classroom lighting conditions ($\mu = 35$), conventional fixed thresholds ($\tau_0 = 0.60$) suffer from severe feature vector distortion, leading to a high False Rejection Rate ($FRR = 66.7\%$). The proposed dynamic threshold $\tau(Q) = \tau_{base} + \lambda(1 - Q)$ relaxes the matching barrier proportionally to image quality loss, lowering the missed attendance rate from $16.7\%$ to **$4.5\%$**.

---

## 6.2 Analysis of Insignificant Changes & System Trade-Offs

1. **Frontal High-Quality Face Recognition:** Under ideal lighting ($\mu = 140$) and frontal pose ($0^\circ$), both the Baseline and Proposed systems achieve **$100.0\%$ accuracy**. This indicates that dynamic thresholding imposes zero accuracy degradation under ideal conditions.
2. **Computational Overhead vs. Real-Time Performance:** The Proposed QMF system introduces a minimal latency penalty (+1.48 ms per frame), increasing frame processing time from $2.56\text{ ms}$ to $4.04\text{ ms}$. However, with a rendering throughput of **$247.3\text{ FPS}$**, the pipeline comfortably exceeds the $30\text{ FPS}$ real-time video streaming requirement.

---

## 6.3 Limitations & Edge Case Failures

1. **Extreme Low Resolution ($< 45\times45\text{px}$):** When a student is seated far from the camera lens ($> 5\text{ meters}$), the bounding box resolution falls below the $40\text{px}$ quality threshold, triggering `QUALITY_REJECTED`. While this prevents false positive matching on noisy pixels, it requires the student to move closer to the kiosk lens.
2. **Extreme Head Pose Angle ($> 35^\circ$ Yaw):** At extreme side-profile angles ($> 35^\circ$), landmark alignment degrades, reducing feature vector similarity below the adaptive threshold.

---

## 6.4 Unexpected Observations

1. **Moiré Glare Artifact Detection:** High-frequency FFT analysis combined with value-channel saturation proved unexpectedly effective at distinguishing high-resolution 4K smartphone screen replays from genuine skin texture without requiring heavy 3D depth cameras or IR sensors.
