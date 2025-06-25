## 📘 ER図（退部対応・Markdown版）

### 🧑‍💻 `User`（ログイン・ロール管理）

| カラム名       | 型             | 説明                                 |
|----------------|----------------|--------------------------------------|
| id             | PK             | ユーザーID（全ユーザー共通）         |
| username       | string         | ログイン名                           |
| email          | string         | メールアドレス                       |
| password       | string         | パスワード（ハッシュ）               |
| role           | enum           | `player` / `manager` / `coach` / `director` |
| created_at     | datetime       | 作成日時                             |
| updated_at     | datetime       | 更新日時                             |

---

### 🧑‍🎓 `StudentProfile`（生徒共通プロフィール）

| カラム名       | 型             | 説明                                 |
|----------------|----------------|--------------------------------------|
| id             | PK             | プロファイルID                       |
| user_id        | FK → User.id   | 紐づくユーザー                       |
| grade          | int            | 学年                                 |
| class_number   | string         | クラス番号                           |
| joined_at      | date           | 入部日                               |
| status         | enum           | `active` / `retired` / `graduated` / `suspended` |
| left_at        | date (nullable)| 退部・卒業・休部日                   |
| leave_reason   | text (nullable)| 退部理由など任意情報                 |

---

### ⚾ `PlayerProfile`（選手のみ）

| カラム名       | 型                   | 説明                     |
|----------------|----------------------|--------------------------|
| id             | PK                   |                          |
| student_id     | FK → StudentProfile.id | 紐づく生徒               |
| position       | string               | ポジション（投手など）  |
| jersey_number  | int                  | 背番号                   |

---

### 📊 `MeasurementRecord`（測定記録）

| カラム名       | 型                   | 説明                                         |
|----------------|----------------------|----------------------------------------------|
| id             | PK                   | 測定記録ID                                   |
| player_id      | FK → PlayerProfile.id| 対象選手                                     |
| measured_at    | date                 | 測定日                                       |
| status         | enum                 | `draft` / `awaiting_player_approval` / `awaiting_coach_approval` / `approved` |
| created_by     | FK → User.id         | 登録者（マネージャー）                      |
| created_at     | datetime             | 作成日時                                     |
| updated_at     | datetime             | 更新日時                                     |

---

### 🧪 `MeasurementItem`（各測定項目）

| カラム名       | 型                    | 説明                  |
|----------------|-----------------------|-----------------------|
| id             | PK                    |                       |
| record_id      | FK → MeasurementRecord.id | 対応する記録            |
| category       | enum                  | `走力` / `打力`など     |
| item_name      | string                | 例: `50m走`, `遠投`     |
| value          | float/int             | 測定値                |
| unit           | string                | 単位 (`sec`, `kg`, etc.)|

---

### ✅ `ApprovalStatus`（承認フロー）

| カラム名       | 型                   | 説明                                |
|----------------|----------------------|-------------------------------------|
| id             | PK                   |                                     |
| record_id      | FK → MeasurementRecord.id | 対応する記録                     |
| approver_id    | FK → User.id         | 承認者（部員→コーチ）              |
| role           | enum                 | `player`, `coach`                   |
| status         | enum                 | `pending`, `approved`, `rejected`   |
| approved_at    | datetime (nullable)  | 承認日時                            |
| comment        | text (nullable)      | 否認時のコメントなど                |
