# DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL

**Version:** 2.1  
**Source:** `bigunandrey/fire-protection-engine/docs/normative/DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL.md`  
**Source SHA:** `64338fb906bb5fc3f2d49130ed16b04b1893b3e0`  
**Migrated:** 2026-09-14  
**Status:** ACTIVE / SOURCE-OF-TRUTH PROCESS

> This document is the migrated normative process specification for converting normative source documents into verified digital representations. The requirements below are preserved from the Fire Protection Engine source protocol. NDI-specific implementation status is tracked separately in `docs/IMPLEMENTATION-STATUS-DIGITAL-NORMATIVE-PROTOCOL.md`.

## 1. Призначення

Цей протокол визначає обов'язковий порядок перетворення нормативного документа (ДБН, ДСТУ, ДСТУ EN, ISO, IEC, NFPA, закон, наказ, технічний регламент тощо) у **цифрову копію**, придатну для машинного пошуку, трасування, перевірки та подальшого виконання нормативної логіки програмним забезпеченням або AI.

Ціль — отримати не просто OCR-текст і не конспект документа, а повну machine-readable representation, у якій кожна нормативна вимога має зв'язок із первинним джерелом, збережений нормативний оператор, умови застосування, винятки, залежності, зміни, видалення та статус перевірки.

Протокол є універсальним і застосовується до нових нормативних документів незалежно від предметної області.

## 2. Визначення цифрової копії

Цифрова копія — сукупність артефактів, яка забезпечує ланцюжок:

```text
source_anchor
  → source_text
  → semantic_rule / table_record / formula_record
  → normative_operator
  → dependencies
  → applicability / type links
  → numeric / formula links
  → verification status
  → change / deletion status
```

Цифрова копія не є простим OCR PDF, переказом документа, таблицею «для зручності», набором припущень AI або виправленою редакцією, де AI самостійно усунув неоднозначності.

## 3. Непорушні принципи

### 3.1 Source of truth

Першочерговим джерелом є актуальна нормативна редакція, яка юридично застосовується для поставленої задачі.

Фіксуються назва, позначення, дата, редакція, дата чинності, зміни, офіційне джерело, дата отримання та SHA-256 вихідного файла.

### 3.2 OCR не є нормативним джерелом

OCR, PDF text extraction, HTML extraction та інші автоматичні способи отримання тексту є лише шаром вилучення.

Критичні елементи перевіряються за графічним оригіналом: таблиці, формули, індекси, степені, оператори `<`, `>`, `≤`, `≥`, `=`, числа, одиниці, примітки, виноски, `+`, `*`, `–`, нумерація, зміни та видалення.

### 3.3 Заборонено тихо виправляти нормативний текст

Якщо джерело містить помилку, прогалину, суперечність, неоднозначну межу, OCR-аномалію або різні формулювання у різних джерелах, AI не має права самостійно перетворювати її на однозначну норму.

Проблема фіксується як `REVIEW_REQUIRED`, `NORMATIVE_GAP`, `SOURCE_DISCREPANCY` або інший відповідний статус.

### 3.4 Нормативні оператори мають бути збережені

`<` ≠ `≤`; `>` ≠ `≥`; `=` ≠ приблизне значення.  
«понад X» = `> X`; «X і більше» = `≥ X`; «до X включно» = `≤ X`.

Не можна змінювати межу лише тому, що інша межа здається логічнішою.

### 3.5 Fail-closed

Якщо для виконання правила бракує нормативно підтвердженого параметра, система не вигадує його. Допустимі результати: `REVIEW_REQUIRED`, `MISSING_INPUT`, `NORMATIVE_GAP` із зазначенням причини та source anchor.

### 3.6 AI inference ≠ нормативна вимога

AI може формувати гіпотезу, кандидатне значення, пропозицію інтерпретації або список перевірок. Це не може бути записано як нормативна вимога без підтвердження джерелом.

## 4. Два обов'язкові master-файли нормативної бази

Обов'язково підтримуються два пов'язані master-файли:

```text
NORMATIVE-DOCUMENT-REGISTER-SPZ-UKRAINE.md
NORMATIVE-DOCUMENT-REGISTER-SPZ-UKRAINE.xlsx
```

### 4.1 MD master register

`NORMATIVE-DOCUMENT-REGISTER-SPZ-UKRAINE.md` — machine-readable та version-controlled реєстр складу і стану нормативної бази. Він містить перелік документів, роль, статус чинності, редакцію/зміни, офіційні джерела, digital status, незалежні AI-перевірки, cross-check, пріоритет та відомі discrepancies / нормативні прогалини.

### 4.2 XLSX operational register

`NORMATIVE-DOCUMENT-REGISTER-SPZ-UKRAINE.xlsx` — операційний контрольний реєстр. Він контролює щонайменше ID, документ, тип, чинність, редакцію/зміни, дату перевірки, офіційне джерело, роль, пріоритет, Digital status, шлях digital copy, AI #1/#2, дати, кількість незалежних перевірок, cross-check, source hash, digital hash/revision, gaps/discrepancies та примітки.

Аркуш `Контроль` використовується для оперативного контролю, `Інструкція` — для правил ведення.

### 4.3 Обов'язкова синхронізація

Якщо змінюється статус документа, цифрової копії, верифікації або cross-check, **MD і XLSX повинні бути узгоджені**.

Не допускається, наприклад:

```text
MD: AI #2 verified
XLSX: AI #2 empty
```

Якщо оновити XLSX фізично неможливо, створюється explicit handoff task для іншого AI/оператора. Handoff не вважається виконаним оновленням; статус залишається `UPDATE_PENDING` до фізичної синхронізації.

## 5. Організація GitHub

Для кожного нормативного документа створюється окрема ізольована папка в `reference-data/`:

```text
reference-data/
└── <DOCUMENT_ID>/
    ├── README.md
    ├── source/
    │   ├── original.<ext>
    │   ├── source-metadata.md
    │   └── source-hash.md
    ├── extracted/
    │   ├── text.txt
    │   └── extraction-log.md
    ├── digital/
    │   ├── rules/
    │   ├── tables/
    │   ├── formulas/
    │   ├── registry/
    │   └── dependencies/
    └── verification/
        ├── graphical/
        ├── external-sources/
        ├── cross-check/
        └── regression/
```

Нормативна документація моделі зберігається в `docs/normative/<document-slug>/`. Master-файли нормативної бази — безпосередньо в `docs/normative/`.

## 6. Архів AI revisions / independent verification records

### 6.1 Призначення

Усі результати незалежних AI-перевірок, ревізій, cross-check, виявлених discrepancies, handoff-завдань та інших матеріалів, які можуть вплинути на статус або зміст цифрової копії, повинні зберігатися **окремо від робочої нормативної документації**.

Це архів доказів і відтворення процесу. Він не замінює source-of-truth, digital copy або master register.

### 6.2 Структура

Стандартна папка:

```text
docs/normative/AI-Revisions/
└── Rev_<NNN>_<DOCUMENT_ID>_<YYYY-MM-DD>/
    ├── <verification-or-register-record>.md
    ├── <additional-record>.md
    └── ...
```

Для поточного проекту приклад:

```text
docs/normative/AI-Revisions/
└── Rev_001_DBN_V_2_5-56_2026-09-04/
```

### 6.3 Правило однієї ревізії

Кожен незалежний цикл ревізії отримує власний номер `Rev_<NNN>`. Номер не перевикористовується.

Одна ревізія може містити кілька файлів одного циклу: verification record, update proposal, discrepancy register, handoff task, source comparison тощо.

### 6.4 Незмінність історії

Записи ревізій не перезаписуються для «очищення» історії. Якщо висновок змінено, створюється новий запис або нова ревізія з посиланням на попередній запис.

Початковий результат AI зберігається навіть якщо подальша перевірка встановила, що частина його висновків була помилковою.

### 6.5 Обов'язкові метадані ревізії

За можливості кожен verification/revision record повинен містити:

```text
revision_id
reviewed_document
reviewed_digital_revision
source_hash
reviewer_ai
review_type
review_date
source_checked
source_urls
independent_sources
scope
checks_performed
discrepancies
resolution_status
result
recommended_master_register_changes
handoff_tasks
```

Якщо певне поле недоступне, воно позначається `NOT_RECORDED`, а не вигадується.

### 6.6 Зв'язок із master register

Кожна ревізія, що впливає на нормативний документ, повинна мати посилання з master register на відповідну папку/файл ревізії. У самій ревізії повинно бути зазначено, який запис master register вона повинна змінити або перевірити.

## 7. Правило початку роботи AI з нормативним документом

Перед будь-якою верифікацією, цифровізацією, cross-check або оновленням AI ОБОВ'ЯЗКОВО читає:

1. `docs/normative/DIGITAL-NORMATIVE-DOCUMENT-PROTOCOL.md`;
2. `docs/normative/NORMATIVE-DOCUMENT-REGISTER-SPZ-UKRAINE.md`;
3. `docs/normative/NORMATIVE-DOCUMENT-REGISTER-SPZ-UKRAINE.xlsx` — якщо доступний;
4. README/manifest конкретного документа;
5. попередні verification/audit artifacts;
6. **архів `docs/normative/AI-Revisions/` для цього документа**, якщо існують попередні ревізії.

AI не починає роботу, орієнтуючись лише на PDF або результат іншого AI.

### 7.1 Перевірка стану перед роботою

AI визначає:

```text
document ID
current validity status
current edition
applicable amendments
existing digital status
existing verification count
previous verifier(s)
last verification date
source hash
current digital copy revision/hash
open discrepancies
open normative gaps
open AI revisions
```

Після цього визначається конкретний scope нової роботи.

## 8. Етап 0 — Ідентифікація джерела

Визначити повну назву, номер, видавця, дату затвердження, дату чинності, поточну редакцію, зміни, дату чинності кожної зміни, офіційний URL, альтернативні відкриті джерела та SHA-256 вихідного файла.

Оновити master register, якщо ці дані відсутні або змінилися.

## 9. Етап 1 — Захоплення первинного джерела

Зберегти доступну первинну редакцію без модифікації. Якщо оригінальний файл неможливо зберегти через формат або обмеження, зафіксувати URL, дату отримання, metadata та hash доступного джерела.

## 10. Етап 2 — Повне вилучення

Виконати повне text extraction та зафіксувати extraction log. Не вважати extracted text нормативно перевіреним.

## 11. Етап 3 — One-to-one decomposition

Розкласти документ без зміни змісту на атомарні нормативні одиниці: пункти, підпункти, абзаци, переліки, примітки, таблиці, комірки, формули, умови, винятки та видалені положення.

Кожна одиниця повинна мати source anchor.

## 12. Етап 4 — Semantic normalization

Для кожної атомарної норми визначити, не змінюючи її зміст:

```text
source
scope
inputs
predicate
normative_operator
action
result
exceptions
notes
dependencies
status
```

Заборонено перетворювати рекомендацію на обов'язок або навпаки.

## 13. Етап 5 — Таблиці

Таблиці декомпозуються до нормативних комірок/рядків із збереженням заголовків, умов застосування, приміток та виносок.

Особливі позначення (`+`, `*`, `–`, `+1`, `+2` тощо) зберігаються буквально до повної цифровізації їхніх приміток.

Потрібно зберігати точні оператори та межі: `усі приміщення`, `незалежно`, `понад X`, `X і більше`, `до X включно` тощо.

## 14. Етап 6 — Формули

Кожна формула зберігається графічно перевіреним і machine-normalized записом із усіма змінними, коефіцієнтами, одиницями та умовами застосування.

Не допускається зміна математичного змісту через OCR або «логічне виправлення».

## 15. Етап 7 — Зміни та видалення

Кожна застосовна зміна має бути відображена в цифровій копії. Видалені пункти не зникають безслідно: вони фіксуються як `DELETED` із зазначенням зміни, яка їх видалила.

Поточна редакція має пріоритет над історичною, але історичний статус зберігається для трасування.

## 16. Етап 8 — Cross-check відкритих джерел

Перевірити ключові норми за офіційними та незалежними відкритими джерелами. Вторинні джерела використовуються насамперед як detector discrepancies, а не як заміна нормативного джерела.

Кожна розбіжність фіксується із зазначенням джерел, anchor, характеру різниці та статусу resolution.

## 17. Етап 9 — Графічна перевірка

Графічній перевірці підлягають щонайменше таблиці, формули, критичні числові значення, оператори, виноски, нумерація, зміни та видалення.

Якщо AI не має доступу до графічного оригіналу, це прямо фіксується як `graphical_check: false`, а висновок не повинен видаватися за повну графічну верифікацію.

## 18. Етап 10 — Dependency mapping

Кожне правило, яке залежить від іншого нормативного документа, стандарту, таблиці, формули, виробника або зовнішнього параметра, отримує явний dependency link.

Нормативні залежності та manufacturer dependencies не змішуються.

## 19. Етап 11 — Незалежна AI-верифікація

Для `DIGITAL_ACCEPTED` потрібні щонайменше **2 незалежні AI verification records**.

Незалежна перевірка означає окремий аналіз цифрової копії із самостійним зверненням до джерела/джерел, а не механічне підтвердження висновків попереднього AI.

Кожна така перевірка обов'язково створює artifact у `docs/normative/AI-Revisions/Rev_<NNN>_<DOCUMENT_ID>_<DATE>/`.

### 19.1 Результат verification

Можливі результати:

```text
ACCEPTED
REVIEW_REQUIRED
NORMATIVE_GAP
SOURCE_DISCREPANCY
UPDATE_PENDING
```

`ACCEPTED` не означає, що нормативний документ позбавлений неоднозначностей; це означає, що цифрова копія відповідає встановленому acceptance criterion з явним статусом відомих gaps.

### 19.2 AI не закриває власну помилку мовчки

Якщо подальша перевірка спростовує попередній висновок, попередній artifact не змінюється. Створюється новий record із посиланням на попередній.

## 20. Master register update після кожної AI-верифікації

Після кожної AI-верифікації потрібно:

1. зберегти verification artifact в AI-Revisions;
2. оновити `NORMATIVE-DOCUMENT-REGISTER-SPZ-UKRAINE.md`;
3. оновити `NORMATIVE-DOCUMENT-REGISTER-SPZ-UKRAINE.xlsx`;
4. синхронізувати MD/XLSX із цифровою копією;
5. перевірити, що verification count, verifier, date, status, cross-check та discrepancy links збігаються.

Якщо фізичне редагування XLSX неможливе, verification record повинен містити explicit handoff task із точними полями, старими і новими значеннями та шляхом до evidence.

До фізичного виконання handoff статус залишається `UPDATE_PENDING`.

## 21. Handoff protocol

Handoff task повинен містити:

```text
TASK
Document
Revision ID
Target file(s)
Exact field(s)
Current value
Required new value
Verifier
Verification date
Result
Evidence path
Reason
Post-update verification steps
```

Інший AI/оператор після виконання зобов'язаний зберегти оновлений MD/XLSX та підтвердити синхронізацію.

## 22. Regression

Після внесення змін у цифрову копію обов'язково виконати regression усіх пов'язаних правил, таблиць, формул, applicability/type links та downstream logic.

Попередній позитивний regression не переноситься автоматично на нову редакцію документа або новий source hash.

## 23. Source hash / revision lock

Кожна accepted digital copy прив'язується до source hash та digital revision/hash. Зміна source hash або застосовної редакції автоматично переводить залежні verification records у стан, що потребує повторної оцінки.

## 24. Final acceptance

Фінальна цифрова копія приймається лише якщо виконано acceptance chain:

```text
source_anchor
→ source_text
→ semantic_rule / table / formula
→ normative_operator
→ dependencies
→ applicability / type links
→ numeric / formula links
→ verification status
→ change / deletion status
→ AI verification records
→ master MD/XLSX synchronization
→ regression
```

Мінімальний критерій `DIGITAL_ACCEPTED`:

- актуальне джерело і hash зафіксовані;
- one-to-one decomposition виконано;
- semantic/table/formula layers закриті в межах scope;
- changes/deletions відображені;
- critical graphical elements verified або явно позначені як unavailable;
- cross-check виконаний або gaps явно зареєстровані;
- ≥2 незалежні AI verification records;
- MD і XLSX синхронні;
- open discrepancies/gaps не приховані;
- regression виконаний;
- AI-Revisions artifacts збережені.

## 25. Статуси

Основні статуси цифровізації:

```text
NOT_STARTED
SOURCE_CAPTURED
EXTRACTED
STRUCTURED
SEMANTIC
TABLES_COMPLETE
FORMULAS_COMPLETE
GRAPHICALLY_VERIFIED
CROSS_CHECKED
DIGITAL_ACCEPTED
REVIEW_REQUIRED
NORMATIVE_GAP
UPDATE_PENDING
SOURCE_DISCREPANCY
DELETED
```

Статус `DIGITAL_ACCEPTED` не може бути використаний для документа, якщо обов'язкові acceptance criteria не виконані.

## 26. Правило відтворюваності

Будь-який суттєвий висновок AI, який вплинув на digital status, master register, нормативне правило, таблицю, формулу, dependency або regression, повинен бути відтворюваним через збережені artifacts.

Має бути можливо встановити:

```text
ХТО
КОЛИ
ЩО ПЕРЕВІРЯВ
ЯКУ РЕДАКЦІЮ
З ЯКИМ SOURCE HASH
ЯКІ ДЖЕРЕЛА ВИКОРИСТАВ
ЩО ЗНАЙШОВ
ЯКИЙ СТАТУС ВСТАНОВИВ
ЯКІ ФАЙЛИ ЗМІНИВ
ЯКИЙ HANDOFF СТВОРИВ
ЯКИЙ НАСТУПНИЙ RECORD ЗАКРИВ/СПРОСТУВАВ ВИСНОВОК
```

Саме для цього існує `docs/normative/AI-Revisions/`.

## 27. AI operating instruction

AI повинен виконувати роботу **послідовно до фактичного результату**, а не зупинятися на плані, шаблоні або переліку наступних кроків.

Перед завершенням роботи AI повинен перевірити:

- чи всі створені artifacts записані у визначені папки;
- чи оновлені master MD/XLSX;
- чи створений revision artifact;
- чи є explicit status;
- чи немає тихих виправлень або прихованих gaps;
- чи збережені source anchors;
- чи виконаний необхідний regression;
- чи може інший AI відтворити проведену перевірку.

Якщо фізична дія неможлива, AI створює explicit handoff замість того, щоб стверджувати, що дія виконана.
