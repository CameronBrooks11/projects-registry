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
    
    <div class="project-count" style="margin:16px 0 8px 0;font-size:0.9rem;opacity:0.7;">
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

<style scoped>
.project-list {
    margin-top: 16px;
    border: 1px solid var(--vp-c-divider);
    border-radius: 8px;
    overflow: hidden;
}

.project-header,
.project-row {
    display: grid;
    grid-template-columns: 2fr 0.8fr 1fr 1fr 0.8fr 1.2fr;
    gap: 16px;
    padding: 12px 16px;
    align-items: start;
}

.project-header {
    background: var(--vp-c-bg-soft);
    border-bottom: 1px solid var(--vp-c-divider);
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    opacity: 0.8;
}

.project-row {
    border-bottom: 1px solid var(--vp-c-divider-light);
    transition: background-color 0.2s;
}

.project-row:last-child {
    border-bottom: none;
}

.project-row:hover {
    background: var(--vp-c-bg-soft);
}

/* Project Name Column */
.project-name {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 4px;
    color: var(--vp-c-text-1);
}

.project-notes {
    font-size: 0.8rem;
    color: var(--vp-c-text-2);
    margin-bottom: 6px;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.project-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 4px;
}

.tag {
    font-size: 0.7rem;
    background: var(--vp-c-bg-soft);
    border: 1px solid var(--vp-c-divider);
    border-radius: 12px;
    padding: 1px 6px;
    color: var(--vp-c-text-2);
}

.tag-more {
    font-size: 0.7rem;
    color: var(--vp-c-text-3);
    font-style: italic;
}

/* Type Column */
.type-badge {
    background: var(--vp-c-brand-soft);
    color: var(--vp-c-brand-dark);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: capitalize;
}

/* Implementation Column */
.impl-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.impl-item {
    font-size: 0.8rem;
    color: var(--vp-c-text-2);
    text-transform: capitalize;
}

/* Target Column */
.target-list {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.target-item {
    font-size: 0.75rem;
    background: var(--vp-c-bg-soft);
    border: 1px solid var(--vp-c-divider);
    border-radius: 3px;
    padding: 1px 4px;
    color: var(--vp-c-text-2);
    font-family: monospace;
}

.target-more {
    font-size: 0.7rem;
    color: var(--vp-c-text-3);
    font-style: italic;
}

/* Status Column */
.status-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.maturity {
    font-size: 0.8rem;
    color: var(--vp-c-text-2);
    text-transform: capitalize;
}

.status {
    font-size: 0.75rem;
    color: var(--vp-c-text-3);
    text-transform: capitalize;
}

/* Links Column */
.link-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}

.link-btn {
    font-size: 0.75rem;
    padding: 2px 6px;
    border-radius: 3px;
    text-decoration: none;
    font-weight: 500;
    border: 1px solid;
    transition: all 0.2s;
}

.link-btn.repo {
    background: var(--vp-c-brand-soft);
    color: var(--vp-c-brand-dark);
    border-color: var(--vp-c-brand);
}

.link-btn.docs {
    background: var(--vp-c-green-soft);
    color: var(--vp-c-green-dark);
    border-color: var(--vp-c-green);
}

.link-btn.issues {
    background: var(--vp-c-yellow-soft);
    color: var(--vp-c-yellow-dark);
    border-color: var(--vp-c-yellow);
}

.link-btn:hover {
    opacity: 0.8;
}

/* Responsive Design */
@media (max-width: 1024px) {
    .project-header,
    .project-row {
        grid-template-columns: 2fr 1fr 1fr;
        gap: 12px;
    }
    
    .col-impl,
    .col-target,
    .col-status {
        display: none;
    }
    
    .project-header .col-impl,
    .project-header .col-target,
    .project-header .col-status {
        display: none;
    }
}

@media (max-width: 768px) {
    .project-header,
    .project-row {
        grid-template-columns: 1fr;
        gap: 8px;
    }
    
    .project-header {
        display: none;
    }
    
    .project-row {
        padding: 16px;
    }
    
    .col-type,
    .col-links {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 8px;
    }
    
    .col-type::before {
        content: "Type:";
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--vp-c-text-2);
    }
    
    .col-links::before {
        content: "Links:";
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--vp-c-text-2);
    }
}
</style>
