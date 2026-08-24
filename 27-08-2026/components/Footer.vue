<template>
  <AlchemmistFooter logo-src="/assets/yandex-logo.webp" :hide-date="hideDate">
    <template #left>
      <div class="footer-project">
        <a
          class="footer-blog"
          href="https://alchemmist.xyz?utm_source=slides"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Блог Антона Гришина"
        >
          <img src="/assets/alchemmist-logo.svg" alt="Alchemmist" />
        </a>
        <a
          class="footer-yandex"
          href="https://yandex-team.ru/atushka/clubs/logs"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Клуб Logs в Этушке"
        >
          <img src="/assets/yandex-logo.webp" alt="Яндекс" />
        </a>
        <a
          class="footer-github"
          href="https://github.com/alchemmist/format-quorum"
          target="_blank"
          rel="noopener noreferrer"
        >
          <carbon:logo-github />
          <span>alchemmist/format-quorum</span>
        </a>
        <a
          class="footer-telegram"
          href="https://t.me/alchemmist"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Telegram @alchemmist"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M23.91 3.79 20.3 20.84c-.27 1.2-.98 1.49-1.99.93l-5.5-4.05-2.65 2.55c-.29.29-.54.54-1.1.54l.39-5.6L19.65 6c.44-.39-.1-.61-.68-.22L6.37 13.72.94 12.02c-1.18-.37-1.2-1.18.25-1.75L22.4 2.09c.98-.36 1.84.24 1.51 1.7z"
            />
          </svg>
          <span>@alchemmist</span>
        </a>
      </div>
    </template>
    <template #right>
      <span v-if="!hideDate && date" class="mono-text">{{ date }}</span>
    </template>
  </AlchemmistFooter>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSlideContext } from "@slidev/client";

const { $slidev, $frontmatter } = useSlideContext();
const date = computed(() => $frontmatter.date ?? $slidev.configs.date ?? "");
const hideDate = computed(() => $frontmatter.hideDate ?? false);
</script>

<style scoped>
.footer-project,
.footer-project a {
  align-items: center;
  display: flex;
}

.footer-project {
  gap: 2.7rem;
}

.footer-project img {
  height: 1.7rem;
}

.footer-blog img {
  height: 1.65rem;
  width: 1.65rem;
}

.footer-project a {
  color: var(--slidev-footer-color, #555);
  font-family: var(--slidev-code-font-family);
  font-size: 0.78rem;
  gap: 0.35rem;
  text-decoration: none;
}

.footer-project a:hover {
  color: #24292f;
}

.footer-project svg {
  height: 1.5rem;
  width: 1.5rem;
}

.footer-project .footer-github,
.footer-project .footer-telegram {
  font-size: calc(0.78rem + 1px);
}

.footer-telegram svg {
  width: 1.2rem;
  height: 1.2rem
}

.footer-github svg {
  width: 1.6rem;
  height: 1.6rem;
}
</style>
