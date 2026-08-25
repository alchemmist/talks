---
theme: alchemmist
addons:
  - fancy-arrow
title: "Приручаем clang-format: как появился Format Quorum — Антон Гришин"
info: |
  Внутренний доклад в Яндексе о новом проекте Format Quorum — инструменте
  для экспериментов с автоформатированием, фиксации регрессий и согласования стиля.
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
Открываю с личной истории: я хотел настроить один форматтер, а в итоге написал отдельный инструмент.
Не обещаю идеальный стиль. Покажу, как сделать спор о стиле проверяемым.
-->

---
layout: center
hide: true
---

# Что вообще могло пойти не так?

<div class="metric-changes">
  <span class="added">+414&#8239;680</span>
  <span class="removed">−340&#8239;127</span>
</div>

<!--
Источники: 47 внутренних PR — 414 680 добавлений и 340 127 удалений суммарно. Полный список и расчёт: scripts/sum_arcanum_diffstats.py.
Это не метрика продуктивности, а масштаб изменения, которое невозможно осмысленно проверить построчно.
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
  <div><div>Большая <span class="mono-text">C++</span> кодовая база</div><span>тысячи файлов в общем репозитории нескольких команд</span></div>
  <div><div>Десятки разработчиков</div><span>в командах со сформированным стилем</span></div>
  <div><div>Отсутствие автоформатирования</div><span></span></div>
  <div><div>Общие решения Яндекса</div><span>с которыми нужно было интегрироваться</span></div>
</div>

::right::

<StickerBoard class="context-sticker-board" seed="format-quorum-context-9" :gap="4">
  <Sticker v-click><b>54 дня</b><span>от первого PR до закрытия финального тикета</span></Sticker>
  <Sticker v-click><b>66 кейсов</b><span>зафиксированы в регрессионных тестах</span></Sticker>
  <Sticker v-click><b>2 итерации</b><span>переформатирования всей кодовой базы</span></Sticker>
  <Sticker v-click><b><span class="mono-text">git clone llvm</span></b><span>модифицированный clang-format</span></Sticker>
  <Sticker v-click><b>5 тикетов</b><span>в поддержку DevTools</span></Sticker>
  <Sticker v-click><b>1&#8239;225 слов</b><span>добавлено в документацию о форматировании и стиле</span></Sticker>
</StickerBoard>

<style scoped>
.context-list > div > div {
  font-size: calc(1.08rem + 1px);
}

.context-list > div > span {
  font-size: calc(0.84rem + 1px);
}
</style>

<!--
54 дня — с 3 июня, когда был создан первый config PR 13704587, до 27 июля, когда после merge PR 14610373 закрыли LOGS-5979.
У PR 13704587 было 10 опубликованных ревизий.
66 кейсов были зафиксированы в регрессионных тестах.
Пять профильных обращений в DevTools: DEVTOOLSSUPPORT-87826, 88104, 88109, 89634 и 90407.
DEVTOOLSSUPPORT-90347 про MSan и 87777 про доступ к CI в подсчёт не входят.
1 225 слов — word-level diff по PR 13833762, 13904435, 13931060, 14684189 и 14758449; Markdown и README, без fenced code blocks, URL и служебной разметки.
-->

---
layout: center
---

# Проблемы

<v-clicks>

- Корнер-кейсы проявляются только на реальном коде
- Эксперименты с форматтерами слишком медленные
- Новый конфиг ломает уже согласованный стиль
- Команде трудно договориться о едином стиле
- Результат трудно встроить в сборку и style-тесты

</v-clicks>

<style scoped>
li {
  font-size: calc(1em + 1px);
}
</style>

<!--
Клик 1: синтетические примеры не показывают всё разнообразие реального кода команды.
Клик 2: смена конфига, версии или форматтера требовала долгого ручного цикла проверки.
Клик 3: изменение одной опции могло сломать места, стиль которых уже согласовали.
Клик 4: разработчики по-разному представляют единый стиль; решение сложно обсудить и зафиксировать для всей команды.
Клик 5: итоговое решение ещё нужно встроить в сборку, style-тесты и внутренние инструменты.
-->

---
layout: center
footer: false
---

# Решение

<Image class="fq-solution-image" src="/assets/format-quorum-demo.png" width="800%"/>

<div v-click="1" class="fq-tour-label" style="left: 210px; top: 88px;">Песочница</div>
<FancyArrow v-if="$clicks >= 1" color="#e65353" width="3" head-size="13" roughness="0.6" arc="0.12" duration="500" from="(210, 111)" to="(210, 200)" />

<div v-click="2" class="fq-tour-label" style="left: 280px; top: 88px;">Тесты</div>
<FancyArrow v-if="$clicks >= 2" color="#e65353" width="3" head-size="13" roughness="0.6" arc="-0.12" duration="500" from="(280, 111)" to="(280, 200)" />

<div v-click="3" class="fq-tour-label" style="left: 333px; top: 88px;">Конфиг</div>
<FancyArrow v-if="$clicks >= 3" color="#e65353" width="3" head-size="13" roughness="0.6" arc="0.12" duration="500" from="(333, 111)" to="(333, 200)" />

<div v-click="4" class="fq-tour-label" style="left: 518px; top: 88px;">Выбор инструмента</div>
<FancyArrow v-if="$clicks >= 4" color="#e65353" width="3" head-size="13" roughness="0.6" arc="0.1" duration="500" from="(518, 111)" to="(518, 200)" />

<div v-click="5" class="fq-tour-label" style="left: 845px; top: 88px;">Запустить и сравнить</div>
<FancyArrow v-if="$clicks >= 5" color="#e65353" width="3" head-size="13" roughness="0.6" arc="-0.12" duration="500" from="(845, 111)" to="(845, 200)" />

<style scoped>
.fq-solution-image {
  transform: translateY(36px);
}

.fq-tour-label {
  position: absolute;
  z-index: 30;
  transform: translateX(-50%);
  color: #111;
  font-family: var(--slidev-code-font-family);
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  white-space: nowrap;
}
</style>

<!--
Клик 1: показываю Песочницу для одного эксперимента.
Клик 2: перехожу к Тестам — накопленной спецификации поведения.
Клик 3: открываю Конфиг для настройки форматтера.
Клик 4: фиксирую выбор инструмента — язык, форматтер и версия.
Клик 5: запускаю форматирование и сразу сравниваю исходный код с результатом.
-->

---
layout: image-right
image: /assets/tests-overview.png
image-width: 50%
---

# Тесты

<v-clicks>

- Единый контекст запуска: язык, форматтер, версия и конфигурация
- Входной код, ожидаемый и фактический результаты рядом
- Запуск всего набора или отдельного теста со статусами pass, fail и mute
- Создание тестов, заметки, прямые ссылки и полноэкранный просмотр кода
- Матрица тестирования по версиям и конфигурациям

</v-clicks>

<!--
Клик 1: тесты используют единый настраиваемый контекст — язык, форматтер, версия и выбранная конфигурация.
Клик 2: раскрытый тест показывает входной код, ожидаемый и фактический результаты рядом.
Клик 3: можно запустить весь набор или один тест; каждый тест проходит, падает или временно отключён.
Клик 4: тесты создаются прямо в интерфейсе. У каждого есть заметка, стабильный идентификатор и прямая ссылка. Если три колонки тесны, удерживаем Option и наводим курсор на секцию кода — она раскрывается на весь экран крупным шрифтом.
Клик 5: матрица показывает результаты тестов на разных версиях и конфигурациях.
-->

---
layout: center
---

# А ещё…

<Image v-click="1" class="detail-card detail-card--history" src="/assets/config-history-detail.png" width="520px" />
<Image v-click="2" class="detail-card detail-card--matrix" src="/assets/version-matrix-detail.png" width="450px" />
<Image v-click="3" class="detail-card detail-card--versions" src="/assets/clang-format-versions.png" width="310px" />
<Image v-click="4" class="detail-card detail-card--impact" src="/assets/config-impact-detail.png" width="440px" />

<style scoped>
h1 {
  position: absolute;
  top: 38px;
  left: 56px;
  margin: 0;
}

.detail-card {
  position: absolute;
  translate: 0 0;
  transform: rotate(var(--detail-rotation));
  transform-origin: center;
  transition:
    opacity 260ms ease,
    transform 520ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

.detail-card.slidev-vclick-hidden {
  opacity: 0;
  transform: translateY(-110px) rotate(calc(var(--detail-rotation) - 5deg)) scale(0.95);
}

.detail-card--history {
  --detail-rotation: -2deg;
  top: 112px;
  left: 56px;
  z-index: 1;
}

.detail-card--matrix {
  --detail-rotation: 2.5deg;
  top: 55px;
  left: 500px;
  z-index: 2;
}

.detail-card--versions {
  --detail-rotation: 1.5deg;
  top: 224px;
  left: 152px;
  z-index: 3;
}

.detail-card--impact {
  --detail-rotation: -2.5deg;
  top: 254px;
  left: 470px;
  z-index: 4;
}
</style>

<!--
Клик 1: история опубликованных версий конфигурации и возможность загрузить прошлую версию в новый черновик.
Клик 2: матрица показывает поведение тестов на разных версиях и shadow-конфигурациях.
Клик 3: версии clang-format и shadow-конфигурации можно добавлять и удалять прямо из интерфейса.
Клик 4: Check impact заранее показывает, какие кейсы новая конфигурация исправит, а какие сломает.
-->

---
layout: center
class: fq-accent-slide
---

# Format Quorum уже не только про <span class="mono-text">C++</span>

<div class="feature-metrics">
  <div><b>13</b><span>языков</span></div>
  <div><b>14</b><span>встроенных форматтеров</span></div>
  <div><b>200</b><span>кейсов <span class="mono-text">BEFORE → AFTER</span></span></div>
</div>

<div class="chips">
  <span>clang-format</span><span>Ruff</span><span>Black</span><span>rustfmt</span>
  <span>Prettier</span><span>shfmt</span><span>Taplo</span><span>google-java-format</span>
</div>

<!--
Числа проверены по текущему реестру и git-корпусу на 20 августа 2026 года.
В продакшене дополнительно зарегистрирован один пользовательский форматтер.
-->

---
layout: center
---

# Приходите :)

<v-clicks>

- Авторизация и команды
- Вопросы и голосования
- Локальный CLI
- Изоляция бинарников в проде
- Удобнее работать с конфигами

</v-clicks>

<style scoped>
li {
  font-size: calc(1em + 1px);
}
</style>

<!--
Клик 1: для голосований нужна идентичность — авторизация, командные пространства и роли. Это же защищает от небезопасных анонимных изменений и загрузок.
Клик 2: поверх проблемного кейса задаём конкретный вопрос, предлагаем варианты результата и собираем голоса до кворума.
Клик 3: выбранный командой вариант можно автоматически сохранить как expected и превратить в новый регрессионный тест.
Клик 4: открытый issue #20 — отдельный CLI с полной функциональностью офлайн, без сервера: https://github.com/alchemmist/format-quorum/issues/20
Клик 5: issue #18 — авторизация и изоляция пользовательских бинарников; issues #11 и #9 — сборка образов в CI и проверка целостности: https://github.com/alchemmist/format-quorum/issues/18, https://github.com/alchemmist/format-quorum/issues/11, https://github.com/alchemmist/format-quorum/issues/9
Клик 6: issues #6 и #5 — подсветка редактора с учётом синтаксиса конфига и общая конфигурация Prettier: https://github.com/alchemmist/format-quorum/issues/6, https://github.com/alchemmist/format-quorum/issues/5
Бэклог проверен 24 августа 2026 года.
-->

---
layout: qr-links
---

::title::

<h1 class="mono-text">Thanks & QA</h1>

::default::

<QrLink
  icon-src="/assets/format-quorum-favicon.svg"
  href="https://fq.alchemmist.xyz"
  label="Demo"
  alt="QR-код демоверсии Format Quorum"
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
  label="Blog"
  alt="QR-код блога Антона Гришина"
/>
<QrLink
  href="https://alchemmist.github.io/talks/27-08-2026/"
  label="Slides"
  alt="QR-код слайдов доклада о Format Quorum"
/>
<QrLink
  icon-src="/assets/telegram-logo.svg"
  href="https://t.me/alchemmist"
  label="Text me"
  alt="QR-код Telegram @alchemmist"
/>

<!--
Оставляю экран открытым для вопросов. Кликабельны только подписи над QR-кодами.
-->
