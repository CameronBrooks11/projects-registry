<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
    taxonomy: {
        types: string[]
        implementation: string[]
        artifact: string[]
        target: string[]
        maturity: string[]
        status: string[]
    }
}>()

const query = defineModel<string>('query')
const typeSel = defineModel<string>('typeSel')
const implSel = defineModel<string>('implSel')
const targetSel = defineModel<string>('targetSel')
const artifactSel = defineModel<string>('artifactSel')
const maturitySel = defineModel<string>('maturitySel')
const statusSel = defineModel<string>('statusSel')
const sortBy = defineModel<string>('sortBy')

const hasFilters = computed(() =>
    !!(query.value || typeSel.value || implSel.value || targetSel.value ||
       artifactSel.value || maturitySel.value || statusSel.value)
)

function clearAll() {
    query.value = ''
    typeSel.value = ''
    implSel.value = ''
    targetSel.value = ''
    artifactSel.value = ''
    maturitySel.value = ''
    statusSel.value = ''
}
</script>

<template>
    <div class="filter-bar" role="search">
        <label class="sr-only" for="search">Search</label>
        <input id="search" v-model="query" class="ctrl search" placeholder="Search…" type="search" autocomplete="off" />

        <label class="sr-only" for="typeSel">Type</label>
        <select id="typeSel" v-model="typeSel" class="ctrl">
            <option value="">Type: any</option>
            <option v-for="t in taxonomy.types" :key="t" :value="t">{{ t }}</option>
        </select>

        <label class="sr-only" for="implSel">Implementation</label>
        <select id="implSel" v-model="implSel" class="ctrl">
            <option value="">Impl: any</option>
            <option v-for="t in taxonomy.implementation" :key="t" :value="t">{{ t }}</option>
        </select>

        <label class="sr-only" for="artifactSel">Artifact</label>
        <select id="artifactSel" v-model="artifactSel" class="ctrl">
            <option value="">Artifact: any</option>
            <option v-for="t in taxonomy.artifact" :key="t" :value="t">{{ t }}</option>
        </select>

        <label class="sr-only" for="targetSel">Target</label>
        <select id="targetSel" v-model="targetSel" class="ctrl">
            <option value="">Target: any</option>
            <option v-for="t in taxonomy.target" :key="t" :value="t">{{ t }}</option>
        </select>

        <label class="sr-only" for="maturitySel">Maturity</label>
        <select id="maturitySel" v-model="maturitySel" class="ctrl">
            <option value="">Maturity: any</option>
            <option v-for="t in taxonomy.maturity" :key="t" :value="t">{{ t }}</option>
        </select>

        <label class="sr-only" for="statusSel">Status</label>
        <select id="statusSel" v-model="statusSel" class="ctrl">
            <option value="">Status: any</option>
            <option v-for="t in taxonomy.status" :key="t" :value="t">{{ t }}</option>
        </select>

        <label class="sr-only" for="sortBy">Sort</label>
        <select id="sortBy" v-model="sortBy" class="ctrl">
            <option value="name">Sort: Name</option>
            <option value="activity">Sort: Activity</option>
            <option value="last_commit">Sort: Last Commit</option>
        </select>

        <button
            v-if="hasFilters"
            class="ctrl clear-btn"
            type="button"
            @click="clearAll"
            aria-label="Clear all filters"
        >Clear</button>
    </div>
</template>

<style scoped>
/* screen-reader only helper */
.sr-only {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}
</style>
