<template>
  <AlchemmistFooter logo-src="/assets/yandex-logo.webp" :hide-date="hideDate">
    <template #left>
      <div class="footer-project">
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
          href="https://github.com/alchemmist/format-quorum"
          target="_blank"
          rel="noopener noreferrer"
        >
          <carbon:logo-github />
          <span>alchemmist/format-quorum</span>
        </a>
      </div>
    </template>
    <template #right>
      <span v-if="!hideDate && date" class="mono-text">{{ date }}</span>
    </template>
  </AlchemmistFooter>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'

const { $slidev, $frontmatter } = useSlideContext()
const date = computed(() => $frontmatter.date ?? $slidev.configs.date ?? '')
const hideDate = computed(() => $frontmatter.hideDate ?? false)
</script>

<style scoped>
.footer-project,
.footer-project a {
  align-items: center;
  display: flex;
}

.footer-project {
  gap: 1.2rem;
}

.footer-project img {
  height: 1.7rem;
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
</style>
