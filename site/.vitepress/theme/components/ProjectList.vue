<script setup lang="ts">
import { ref, computed } from 'vue'
import data from '../index.json'
import FilterBar from './FilterBar.vue'

type Project = {
    id: string
    name: string
    slug: string
    type: string
    implementation: string[]
    artifact: string[]
    target: string[]
    maturity?: string
    status?: string
    repos?: { host: string, url: string }[]
    links?: Record<string, string>
    tags?: string[]
    notes?: string
}

const query = ref('')
const typeSel = ref<string | ''>('')
const implSel = ref<string | ''>('')
const targetSel = ref<string | ''>('')

const projects = (data.projects as Project[])

const filtered = computed(() => {
    const q = query.value.trim().toLowerCase()
    return projects.filter(p => {
        const textHit = !q || (
            p.name.toLowerCase().includes(q) ||
            (p.tags || []).some(t => t.toLowerCase().includes(q)) ||
            (p.notes || '').toLowerCase().includes(q)
        )
        const typeHit = !typeSel.value || p.type === typeSel.value
        const implHit = !implSel.value || p.implementation?.includes(implSel.value)
        const targetHit = !targetSel.value || p.target?.includes(targetSel.value)
        return textHit && typeHit && implHit && targetHit
    }).sort((a, b) => a.name.localeCompare(b.name))
})
</script>

<template>
    <FilterBar v-model:query="query" v-model:typeSel="typeSel" v-model:implSel="implSel" v-model:targetSel="targetSel"
        :taxonomy="data.taxonomy" />
    <div class="grid"
        style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-top:16px;">
        <article v-for="p in filtered" :key="p.id"
            style="border:1px solid var(--vp-c-divider);border-radius:12px;padding:14px;">
            <h3 style="margin:0 0 6px 0;font-size:1.05rem;">{{ p.name }}</h3>
            <div style="font-size:0.85rem;opacity:0.8;">{{ p.type }} · {{ p.maturity || '—' }} · {{ p.status || '—' }}
            </div>
            <div style="margin-top:8px;font-size:0.85rem;">
                <strong>Impl:</strong> {{ p.implementation?.join(', ') || '—' }}<br />
                <strong>Target:</strong> {{ p.target?.join(', ') || '—' }}
            </div>
            <div v-if="p.tags?.length" style="margin-top:8px;display:flex;flex-wrap:wrap;gap:6px;">
                <span v-for="t in p.tags" :key="t"
                    style="font-size:0.75rem;border:1px solid var(--vp-c-divider);border-radius:999px;padding:2px 8px;">{{
                    t }}</span>
            </div>
            <div v-if="p.repos?.length" style="margin-top:10px;font-size:0.85rem;">
                <a :href="p.repos[0].url" target="_blank" rel="noopener">Repository</a>
            </div>
        </article>
    </div>
</template>
