<script setup lang="ts">
const props = defineProps<{
    taxonomy: {
        types: string[]
        implementation: string[]
        target: string[]
    }
}>()

const query = defineModel<string>('query')
const typeSel = defineModel<string>('typeSel')
const implSel = defineModel<string>('implSel')
const targetSel = defineModel<string>('targetSel')
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

        <label class="sr-only" for="targetSel">Target</label>
        <select id="targetSel" v-model="targetSel" class="ctrl">
            <option value="">Target: any</option>
            <option v-for="t in taxonomy.target" :key="t" :value="t">{{ t }}</option>
        </select>
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
