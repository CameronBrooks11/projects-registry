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
    <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <input v-model="query" placeholder="Search…"
            style="flex:1;min-width:220px;padding:8px;border:1px solid var(--vp-c-divider);border-radius:8px;">
        <select v-model="typeSel" style="padding:8px;border:1px solid var(--vp-c-divider);border-radius:8px;">
            <option value="">Type: any</option>
            <option v-for="t in taxonomy.types" :key="t" :value="t">{{ t }}</option>
        </select>
        <select v-model="implSel" style="padding:8px;border:1px solid var(--vp-c-divider);border-radius:8px;">
            <option value="">Impl: any</option>
            <option v-for="t in taxonomy.implementation" :key="t" :value="t">{{ t }}</option>
        </select>
        <select v-model="targetSel" style="padding:8px;border:1px solid var(--vp-c-divider);border-radius:8px;">
            <option value="">Target: any</option>
            <option v-for="t in taxonomy.target" :key="t" :value="t">{{ t }}</option>
        </select>
    </div>
</template>
