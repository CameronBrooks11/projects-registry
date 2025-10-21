<script setup lang="ts">
import { ref, computed } from 'vue'
import data from '../projects-index.json'
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
    
    <div class="project-count">
        {{ filtered.length }} project{{ filtered.length !== 1 ? 's' : '' }}
    </div>
    
    <div class="project-list">
        <div class="project-header">
            <div class="col-name">Project</div>
            <div class="col-type">Type</div>
            <div class="col-impl">Implementation</div>
            <div class="col-target">Target</div>
            <div class="col-status">Status</div>
            <div class="col-links">Links</div>
        </div>
        
        <div v-for="p in filtered" :key="p.id" class="project-row">
            <div class="col-name">
                <div class="project-name">{{ p.name }}</div>
                <div class="project-notes" v-if="p.notes">{{ p.notes }}</div>
                <div class="project-tags" v-if="p.tags?.length">
                    <span v-for="t in p.tags.slice(0, 4)" :key="t" class="tag">{{ t }}</span>
                    <span v-if="p.tags.length > 4" class="tag-more">+{{ p.tags.length - 4 }}</span>
                </div>
            </div>
            
            <div class="col-type">
                <span class="type-badge">{{ p.type }}</span>
            </div>
            
            <div class="col-impl">
                <div class="impl-list">
                    <span v-for="impl in p.implementation" :key="impl" class="impl-item">{{ impl }}</span>
                </div>
            </div>
            
            <div class="col-target">
                <div class="target-list">
                    <span v-for="target in p.target?.slice(0, 3)" :key="target" class="target-item">{{ target }}</span>
                    <span v-if="(p.target?.length || 0) > 3" class="target-more">+{{ (p.target?.length || 0) - 3 }}</span>
                </div>
            </div>
            
            <div class="col-status">
                <div class="status-info">
                    <div class="maturity">{{ p.maturity || '—' }}</div>
                    <div class="status">{{ p.status || '—' }}</div>
                </div>
            </div>
            
            <div class="col-links">
                <div class="link-buttons">
                    <a v-if="p.repos?.length" :href="p.repos[0].url" target="_blank" rel="noopener" class="link-btn repo">
                        Repo
                    </a>
                    <a v-if="p.links?.docs" :href="p.links.docs" target="_blank" rel="noopener" class="link-btn docs">
                        Docs
                    </a>
                    <a v-if="p.links?.issues" :href="p.links.issues" target="_blank" rel="noopener" class="link-btn issues">
                        Issues
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>

<style src="./ProjectList.css" scoped />
