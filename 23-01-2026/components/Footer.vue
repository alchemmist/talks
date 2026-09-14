<template>
  <AlchemmistFooter
    logo-src="/assets/cu-logo.svg"
    logo-alt="Central University"
  >
    <template #right>
      <div class="footer-meta">
        <a
          href="https://github.com/alchemmist/talks"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Talks repository on GitHub"
        >
          <carbon:logo-github />
        </a>
        <span class="mono-text">{{ date }}</span>
      </div>
    </template>
  </AlchemmistFooter>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSlideContext } from "@slidev/client";

const { $slidev, $frontmatter } = useSlideContext();

const date = computed(() => $frontmatter.date ?? $slidev.configs.date ?? "");
</script>

<style scoped>
.footer-meta {
  align-items: center;
  display: flex;
  gap: 1rem;
}

.footer-meta a {
  display: inline-flex;
  font-size: 1.35rem;
}
</style>
