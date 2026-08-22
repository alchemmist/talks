---
theme: alchemmist
addons:
  - fancy-arrow
title: "Приручаем clang-format: как появился Format Quorum — Антон Гришин"
info: |
  Приватный доклад о том, как настройка форматирования для команды
  превратилась в инструмент для проверки правил и коллективного выбора.
drawings:
  persist: false
duration: 20min
date: 27 августа 2026
remoteAssets: false
pwa: build
themeConfig:
  paginationX: r
  paginationY: t
  footerComponent: Footer

layout: intro
footer: true
pagination: false
---

# Приручаем <span class="mono-text">clang-format</span>:<br />как появился <span class="title-accent">Format Quorum</span>

<div class="title-author">
  <img src="/assets/anton-grishin.png" alt="Антон Гришин" />
  <div>
    <div class="title-author-name">Антон Гришин</div>
    <div class="title-author-team">инфраструктура обработки данных</div>
  </div>
</div>

<!--
Открываю с личной истории: я хотел настроить один formatter, а в итоге написал отдельный инструмент.
Не обещаю идеальный стиль. Покажу, как сделать спор о стиле проверяемым.
-->

---
layout: center
---

# Что вообще могло пойти не так?

<div class="metric-changes">
  <span class="added">+414&#8239;680</span>
  <span class="removed">−340&#8239;127</span>
</div>


<!--
Источники: 47 внутренних PR — 414 680 добавлений и 340 127 удалений суммарно. Полный список и расчёт: scripts/sum_arcanum_diffstats.py.
Это не метрика продуктивности, а масштаб необратимого для ревью решения.
-->

---
layout: center
---

<Quote
  text="They found a statistically significant difference (odds ratio = 4.62, p &lt; 0.05) […] omitting curly braces is associated with misunderstanding. […] 93.3% […] agreed […] hard to read."
  author="Delano Oliveira, Reydne Santos, Fernanda Madeiral, Hidehiko Masuhara, Fernando Castor"
  source="A systematic literature review on the impact of formatting elements on code legibility"
  sourceUrl="https://prg.is.titech.ac.jp/papers/pdf/jss2023.pdf"
  year="2023"
  type="Systematic literature review"
  avatar="/assets/delano-oliveira.jpg"
/>

<!--
Буквальная цитата собрана из фрагментов раздела про block delimiters; пропуски обозначены […] без изменения исходных слов.
Обзор пересказывает эксперимент Langhout и Aniche 2021 года на Java-коде.
Odds ratio 4,62 означает сильную связь между отсутствием фигурных скобок и неправильным пониманием кода; 93,3% участников сочли такой фрагмент трудночитаемым.
Главный тезис для доклада: решения о стиле влияют не только на вкус, но и на вероятность правильно понять код.
-->

---
layout: context-board
gap: 1rem
split: 36%
---

# Контекст

::left::

<div class="context-list">
  <div><div>Большая <span class="mono-text">C++</span> кодовая база</div><span>тысячи файлов в общем репозитории на несколько команд</span></div>
  <div><div>Десятки разработчиков</div><span>в командах с сформированным стилем</span></div>
  <div><div>Отсутствие автоформатирования</div><span></span></div>
  <div><div>Общие решения Яндекса</div><span>с которыми хотелось интегрироваться</span></div>
</div>

::right::

<StickerBoard class="context-sticker-board" seed="format-quorum-context-9" :gap="4">
  <Sticker v-click><b>54 дня</b><span>от первого PR до закрытия финального тикета</span></Sticker>
  <Sticker v-click><b>66 корнер-кейсов</b><span>отлиты в регрессионные тесты</span></Sticker>
  <Sticker v-click><b>2 итерации</b><span>переформатирования всей кодовой базы</span></Sticker>
  <Sticker v-click><b><span class="mono-text">git clone llvm</span></b><span>модифицированный clang-format</span></Sticker>
  <Sticker v-click><b>5 тикетов</b><span>в поддержку DevTools</span></Sticker>
  <Sticker v-click><b>1&#8239;225 слов</b><span>добавлено в документацию о форматировании и стиле</span></Sticker>
</StickerBoard>

<!--
54 дня — с 3 июня, когда создан первый config PR 13704587, до 27 июля, когда после merge PR 14610373 закрыт LOGS-5979.
У PR 13704587 было 10 опубликованных ревизий.
В репозитории хранится 37 <span class="mono-text">C++</span> golden-тестов; ещё 13 baseline-кейсов относятся к Python, поэтому 66 кодом не подтверждается.
Пять профильных обращений в Dev Tools: DEVTOOLSSUPPORT-87826, 88104, 88109, 89634 и 90407.
DEVTOOLSSUPPORT-90347 про MSan и 87777 про доступ к CI в счёт не входят.
1 225 слов — word-level diff по PR 13833762, 13904435, 13931060, 14684189 и 14758449; Markdown и README, без fenced code blocks, URL и служебной разметки.
-->

---
layout: center
---

# Проблемы

<div class="workflow-needs">
  <div v-click><b>Огромное количество корнер-кейсов</b><span>которые обнаруживаются только на реальном коде.</span></div>
  <div v-click><b>Регрессии читаемости</b><span>доработка конфига приводила к ухудшению ранее сформированного стиля</span></div>
  <div v-click><b>Честное сравнение</b><span>прогонять разные конфиги и formatter'ы на одном наборе примеров</span></div>
  <div v-click><b>Командное обсуждение</b><span>показать вариант на встрече, быстро изменить опцию и вместе принять решение</span></div>
</div>

<div v-click class="callout workflow-needs-callout">Нужно было общее пространство для эксперимента, проверки и принятия решения.</div>

<!--
Нужен был не ещё один способ отредактировать конфиг, а полный рабочий цикл.
Эксперимент должен быть быстрым, прошлые договорённости — исполняемыми, сравнение — воспроизводимым, а обсуждение — удобным для всей команды.
-->

---
layout: center
footer: false
---

# Решение

<Image src="/assets/format-quorum-demo.png" width="800%"/>

---
layout: image-right
image: /assets/playground-overview.png
---

# Playground<MarkerX color="#5D3FD3" title="интерфейс" />

- выбрать formatter и его версию
- вставить исходный код
- увидеть результат и line diff
- сохранить состояние в shareable URL

<!--
Показываю слева намеренно плохо оформленный фрагмент, справа — результат выбранной версии.
Состояние formatter, версии, теста и вкладки сохраняется в shareable URL.
-->

---
layout: image-right
image: /assets/tests-overview.png
---

# Тесты правил<MarkerX color="#5D3FD3" title="интерфейс" />

- статусы pass, fail и muted
- запуск одного теста или всего набора
- фактический результат рядом с ожидаемым
- прямая ссылка на конкретный кейс

<!--
Это не unit-тест реализации Format Quorum, а спецификация поведения formatter.
Тест можно запустить отдельно, раскрыть фактический результат, заглушить и отправить прямой ссылкой.
-->

---
layout: image-right
image: /assets/config-editor.png
---

# Конфиг и его влияние<MarkerX color="#5D3FD3" title="интерфейс" />

- выбранная версия formatter'а
- локальный draft в браузере
- сравнение live и candidate
- история и публикация готового изменения

<!--
Правка сначала остаётся в localStorage и применяется к следующим локальным запускам.
Другие пользователи не увидят её до Publish, поэтому эксперимент не затирает общее состояние.
What-if запускает live и candidate config, затем показывает только переходы pass/fail и muted would pass.
-->

---
layout: image-right
image: /assets/version-matrix.png
---

# Version matrix<MarkerX color="#5D3FD3" title="интерфейс" />

- строки — тестовые кейсы
- столбцы — версии и shadow-конфиги
- ячейки — pass, fail или muted
- неожиданный переход сразу бросается в глаза

<!--
Shadow config использует тот же бинарник, но имеет отдельный конфиг и ведёт себя как квази-версия.
Матрица сразу показывает неожиданные регрессии и muted-тесты, которые уже можно включить.
-->

---
layout: image-right
image: /assets/config-history.png
---

# Версии и история<MarkerX color="#5D3FD3" title="интерфейс" />

- опубликованные изменения append-only
- Load возвращает версию в новый draft
- shadow живёт рядом с основной конфигурацией
- сравнение не требует нового бинарника

<!--
Каждое опубликованное изменение конфига становится новой записью истории.
Откат не уничтожает прошлое: выбранная версия загружается как следующий draft.
-->

---
layout: center
class: fq-accent-slide
---

# Format Quorum уже не только про <span class="mono-text">C++</span>

<div class="feature-metrics">
  <div><b>13</b><span>языков</span></div>
  <div><b>14</b><span>встроенных formatter'ов</span></div>
  <div><b>200</b><span>BEFORE → AFTER кейсов</span></div>
</div>

<div class="chips">
  <span>clang-format</span><span>Ruff</span><span>Black</span><span>rustfmt</span>
  <span>Prettier</span><span>shfmt</span><span>Taplo</span><span>google-java-format</span>
</div>

<div class="callout">Formatter, версия и конфиг — независимые оси эксперимента.</div>

<!--
Числа проверены по текущему реестру и git-корпусу на 20 августа 2026.
В production дополнительно зарегистрирован один пользовательский formatter.
-->

---
layout: center
---

# Свой formatter — без форка<MarkerX color="#c87800" title="deployment" />

<div class="custom-binary-lead">Разворачиваете Format Quorum внутри команды — загружайте собственные бинарники.</div>

<div class="custom-binary-flow">
  <div>
    <small>1 · Upload</small>
    <b>Бинарник + версия</b>
    <span>и язык, для которого он работает</span>
  </div>
  <strong>→</strong>
  <div>
    <small>2 · Registry</small>
    <b>Обычный formatter</b>
    <span>со своим runner и конфигом</span>
  </div>
  <strong>→</strong>
  <div>
    <small>3 · Use</small>
    <b>Playground · Tests</b>
    <span>версии, matrix и история</span>
  </div>
</div>

<div class="custom-binary-guard"><code>ALLOW_BINARY_UPLOAD=1</code><span>Только для доверенного локального окружения: загруженный бинарник выполняется на сервере.</span></div>

<!--
Источники: backend/main.py, formatter_registry.py, custom_formatter_store.py и versions.py.
Пользовательский formatter сохраняется, регистрируется в общем Formatter Registry и получает UploadOnlyInstall с собственной осью версий.
Uploads выключены по умолчанию, потому что сервер будет исполнять загруженный код. Для локального доверенного deployment включаются через ALLOW_BINARY_UPLOAD=1.
-->

---
layout: center
---

# Что получилось<MarkerX color="#50C878" title="результат" />

<div class="result-grid">
  <div><b>200</b><span>проверяемых примеров вместо потерянных комментариев</span></div>
  <div><b>13</b><span>языков в одной модели formatter → config → tests</span></div>
  <div><b>37</b><span><span class="mono-text">C++</span>-кейсов, выросших из реальной обратной связи</span></div>
  <div><b>1</b><span>безопасное место для экспериментов до массового PR</span></div>
</div>

<div class="callout">Главный эффект — решения стали воспроизводимыми и сравнимыми.</div>

<!--
Не заявляю экономию времени без измерений.
Подтверждённый результат — структура данных, набор кейсов, поддерживаемые formatter'ы и завершённая доставка patched clang-format.
-->

---
layout: center
---

# Следующий шаг — настоящее quorum<MarkerX color="#5D3FD3" title="планы" />

<div class="quorum-roadmap">
  <div><small>ПРОБЛЕМНЫЙ КОД</small><b>один тест-кейс</b></div>
  <span>→</span>
  <div><small>ВОПРОС</small><b>как он должен выглядеть?</b></div>
  <span>→</span>
  <div><small>ВАРИАНТЫ</small><b>A · B · C</b></div>
  <span>→</span>
  <div class="primary"><small>QUORUM</small><b>голоса команды</b></div>
</div>

<div v-click class="roadmap-outcome">Выбранный вариант становится ожидаемым результатом регрессионного теста.</div>

<!--
Главное направление развития — добавить голосование поверх тест-кейсов.
Можно взять проблемный фрагмент, предложить несколько вариантов результата и собрать решение команды прямо в Format Quorum.
После достижения quorum выбранный вариант фиксируется как expected и дальше защищается регрессионным запуском.
-->

---
layout: qr-links
---

<QrLink
  icon-src="/assets/format-quorum-favicon.svg"
  href="https://fq.alchemmist.xyz"
  label="Format Quorum"
  alt="QR-код live demo Format Quorum"
/>

::right::

<QrLink
  icon-src="/assets/github-logo.svg"
  href="https://github.com/alchemmist/format-quorum"
  display="alchemmist/format-quorum"
  label="GitHub"
  alt="QR-код репозитория Format Quorum на GitHub"
/>
<QrLink
  icon-src="/assets/alchemmist-logo.svg"
  href="https://alchemmist.xyz"
  label="Блог"
  alt="QR-код блога Антона Гришина"
/>

<!--
Оставляю экран открытым для вопросов. Кликабельны только адреса под QR-кодами.
-->
