<script setup lang="ts">
import { computed } from 'vue'
import data from '../pending-index.json'

type PendingProject = {
  id: string
  name: string
  notes: string
  repos?: { host: string; url: string }[]
}

const pending = (data.pending as PendingProject[]) || []

const sortedPending = computed(() =>
  pending.sort((a, b) => a.name.localeCompare(b.name))
)
</script>

<template>
  <div v-if="pending.length > 0" class="pending-section">
    <div class="pending-header">
      <div class="pending-title">PENDING PROJECTS</div>
      <div class="pending-subtitle">
        {{ pending.length }} project{{ pending.length !== 1 ? 's' : '' }} pending addition to the registry
      </div>
    </div>

    <div class="pending-table-wrapper">
      <table class="pending-table">
        <thead>
          <tr>
            <th class="col-pending-name">PROJECT NAME</th>
            <th class="col-pending-notes">DESCRIPTION</th>
            <th class="col-pending-repo">REPOSITORY</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in sortedPending" :key="p.id" class="pending-row">
            <td class="pending-name">
              <div class="pending-project-name">{{ p.name }}</div>
              <div class="pending-project-id">{{ p.id }}</div>
            </td>
            <td class="pending-notes">
              {{ p.notes || 'No description available' }}
            </td>
            <td class="pending-repo">
              <a v-if="p.repos?.length" :href="p.repos[0].url" target="_blank" rel="noopener" class="pending-repo-link">
                VIEW REPO
              </a>
              <span v-else class="no-repo">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style src="./PendingList.css" scoped />
