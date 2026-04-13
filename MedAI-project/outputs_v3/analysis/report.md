# SLAKE 이미지 의존성 분석 리포트

이 문서는 `src.analyze_results`가 생성한 분석 결과를 바탕으로 자동 생성된 요약 리포트입니다.

## 1. Overall Accuracy (Strict)

| condition     |   overall |
|:--------------|----------:|
| original      |  0.470311 |
| black         |  0.236569 |
| lpf           |  0.461828 |
| hpf           |  0.424128 |
| patch_shuffle |  0.248822 |

## 2. Overall Accuracy (Relaxed)

| condition     |   overall |
|:--------------|----------:|
| original      |  0.540999 |
| black         |  0.269557 |
| lpf           |  0.535344 |
| hpf           |  0.492931 |
| patch_shuffle |  0.290292 |

## 3. Answer Type Accuracy (Strict)

| condition     |   closed |      open |
|:--------------|---------:|----------:|
| original      | 0.745192 | 0.293023  |
| black         | 0.485577 | 0.075969  |
| lpf           | 0.745192 | 0.27907   |
| hpf           | 0.701923 | 0.244961  |
| patch_shuffle | 0.540865 | 0.0604651 |

## 4. Answer Type Accuracy (Relaxed)

| condition     |   closed |     open |
|:--------------|---------:|---------:|
| original      | 0.747596 | 0.407752 |
| black         | 0.485577 | 0.130233 |
| lpf           | 0.75     | 0.396899 |
| hpf           | 0.704327 | 0.356589 |
| patch_shuffle | 0.540865 | 0.128682 |

## 5. 자주 생성되는 예측 답변

| pred_answer_normalized   |   count | condition   |
|:-------------------------|--------:|:------------|
| yes                      |     232 | original    |
| no                       |     214 | original    |
| liver                    |      54 | original    |
| brain                    |      39 | original    |
| two                      |      37 | original    |
| lungs                    |      35 | original    |
| left lung                |      28 | original    |
| respiratory              |      26 | original    |
| chest                    |      24 | original    |
| axial                    |      24 | original    |
| ct                       |      22 | original    |
| xray                     |      21 | original    |
| lung                     |      20 | original    |
| mri                      |      18 | original    |
| abdomen                  |      17 | original    |
| heart                    |      14 | original    |
| one                      |      13 | original    |
| left hemisphere          |      12 | original    |
| thorax                   |      11 | original    |
| t2weighted               |      11 | original    |

## 6. Original 조건에서 자주 발생하는 오답 쌍

| gt_answer_normalized   | pred_answer_normalized   |   count |
|:-----------------------|:-------------------------|--------:|
| no                     | yes                      |      46 |
| yes                    | no                       |      31 |
| lung                   | lungs                    |      29 |
| transverse plane       | axial                    |      24 |
| 2                      | two                      |      23 |
| chest                  | respiratory              |      20 |
| head                   | brain                    |      18 |
| 0                      | two                      |      11 |
| breathe                | respiration              |      11 |
| none                   | no                       |       9 |
| black                  | white                    |       7 |
| t2                     | t2weighted               |       7 |
| lower left lung        | left lung                |       7 |
| chest                  | thorax                   |       7 |
| 1                      | one                      |       7 |
| cardiomegaly           | no                       |       6 |
| lung                   | liver                    |       5 |
| right lung             | liver                    |       5 |
| heart                  | lung                     |       4 |
| large bowel            | liver                    |       4 |

## 7. Original 조건에서의 대표 오답 예시

|   image_id |   question_id | question                                                 | gt_answer   | pred_answer   | gt_answer_normalized   | pred_answer_normalized   | answer_type   | q_type      | content_type   | modality   | location   | base_type   | condition   | eval_mode   | is_correct_strict   | is_correct_relaxed   |
|-----------:|--------------:|:---------------------------------------------------------|:------------|:--------------|:-----------------------|:-------------------------|:--------------|:------------|:---------------|:-----------|:-----------|:------------|:------------|:------------|:--------------------|:---------------------|
|        103 |         11949 | Does the picture contain liver?                          | No          | Yes.          | no                     | yes                      | closed        | Organ       | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        124 |         11971 | Which organ is abnormal, heart or lung?                  | Heart       | Lung          | heart                  | lung                     | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | text_match  | False               | False                |
|         13 |         11975 | Is there any abnormality in the spleen?                  | No          | Yes.          | no                     | yes                      | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|         13 |         11976 | Does the liver look normal?                              | Yes         | No.           | yes                    | no                       | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|         13 |         11979 | Does the picture contain spleen?                         | Yes         | No.           | yes                    | no                       | closed        | Organ       | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        135 |         11989 | Are there abnormalities in this image?                   | Yes         | No            | yes                    | no                       | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        142 |         12000 | Which organ is abnormal, heart or lung?                  | Heart       | Lung          | heart                  | lung                     | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | text_match  | False               | False                |
|        148 |         12011 | Are there abnormalities in this image?                   | Yes         | No            | yes                    | no                       | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        148 |         12015 | Which organ is abnormal, heart or lung?                  | Heart       | Lung          | heart                  | lung                     | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | text_match  | False               | False                |
|        152 |         12022 | Which organ is abnormal, heart or lung?                  | Heart       | Lung          | heart                  | lung                     | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | text_match  | False               | False                |
|         18 |         12064 | Does the kidney look abnormal?                           | No          | Yes.          | no                     | yes                      | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        185 |         12074 | Which organ is abnormal, heart or lung?                  | Lung        | Heart         | lung                   | heart                    | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | text_match  | False               | False                |
|        208 |         12080 | Does the picture contain spleen?                         | No          | Yes.          | no                     | yes                      | closed        | Organ       | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        208 |         12085 | Is the liver healthy?                                    | Yes         | No            | yes                    | no                       | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        219 |         12092 | Does this image look normal?                             | Yes         | No.           | yes                    | no                       | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        219 |         12101 | Is the liver healthy?                                    | Yes         | No.           | yes                    | no                       | closed        | Abnormality | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        219 |         12102 | Which is the biggest in this image, lung,heart or liver? | Lung        | Liver         | lung                   | liver                    | closed        | Size        | unknown        | unknown    | unknown    | unknown     | original    | text_match  | False               | False                |
|        224 |         12112 | Does the picture contain lung?                           | Yes         | No            | yes                    | no                       | closed        | Organ       | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        224 |         12113 | Does the picture contain heart?                          | No          | Yes.          | no                     | yes                      | closed        | Organ       | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |
|        234 |         12124 | Does the picture contain kidney?                         | No          | Yes.          | no                     | yes                      | closed        | Organ       | unknown        | unknown    | unknown    | unknown     | original    | yes_no      | False               | False                |

## 8. Original 대비 Black에서 성능이 떨어진 샘플 분포

| answer_type   |   count |
|:--------------|--------:|
| open          |     155 |
| closed        |     153 |

## 9. Original 대비 Patch Shuffle에서 성능이 떨어진 샘플 분포

| answer_type   |   count |
|:--------------|--------:|
| open          |     166 |
| closed        |     124 |

## 10. Original 대비 HPF에서 성능이 떨어진 샘플 분포

| answer_type   |   count |
|:--------------|--------:|
| open          |      42 |
| closed        |      37 |

## 11. 해석 가이드

- `strict`는 exact match 기준이므로 보수적인 지표다.
- `relaxed`는 substring 기준이므로 의미적으로 부분적으로 맞는 답을 일부 허용한다.
- `black`에서 큰 성능 하락이 없으면 텍스트 prior 의존 가능성을 의심할 수 있다.
- `patch_shuffle`에서 성능 하락이 크면 spatial structure 활용 가능성이 있다.
- `open`의 낮은 점수는 모델 자체 한계와 채점 기준의 엄격함이 함께 반영된 결과일 수 있다.
