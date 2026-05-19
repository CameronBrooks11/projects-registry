<script setup lang="ts">
import { ref, computed } from 'vue'
import data from '../projects-index.json'
import FilterBar from './FilterBar.vue'

type Derived = {
    stars: number | null
    forks: number | null
    open_issues: number | null
    last_commit: string | null
    primary_language: string | null
    topics: string[]
    activity_score: number | null
}

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
    repos?: { host: string; url: string }[]
    links?: { docs?: string; issues?: string; site?: string; [key: string]: string | undefined }
    tags?: string[]
    notes?: string
    derived?: Derived
}

const query = ref('')
const typeSel = ref('')
const implSel = ref('')
const targetSel = ref('')
const artifactSel = ref('')
const maturitySel = ref('')
const statusSel = ref('')
const sortBy = ref('name')

const projects = data.projects as Project[]

const filtered = computed(() => {
    const q = query.value.trim().toLowerCase()
    return projects
        .filter(p => {
            const textHit =
                !q ||
                p.name.toLowerCase().includes(q) ||
                (p.tags || []).some(t => t.toLowerCase().includes(q)) ||
                (p.notes || '').toLowerCase().includes(q)
            const typeHit = !typeSel.value || p.type === typeSel.value
            const implHit = !implSel.value || p.implementation?.includes(implSel.value)
            const targetHit = !targetSel.value || p.target?.includes(targetSel.value)
            const artifactHit = !artifactSel.value || p.artifact?.includes(artifactSel.value)
            const maturityHit = !maturitySel.value || p.maturity === maturitySel.value
            const statusHit = !statusSel.value || p.status === statusSel.value
            return textHit && typeHit && implHit && targetHit && artifactHit && maturityHit && statusHit
        })
        .slice()
        .sort((a, b) => {
            if (sortBy.value === 'activity')
                return (b.derived?.activity_score ?? 0) - (a.derived?.activity_score ?? 0)
            if (sortBy.value === 'last_commit')
                return (b.derived?.last_commit ?? '').localeCompare(a.derived?.last_commit ?? '')
            return a.name.localeCompare(b.name)
        })
})

function relativeTime(iso: string | null | undefined): string {
    if (!iso) return '—'
    const days = Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000)
    if (days === 0) return 'today'
    if (days === 1) return 'yesterday'
    if (days < 30) return `${days}d ago`
    if (days < 365) return `${Math.floor(days / 30)}mo ago`
    return `${Math.floor(days / 365)}y ago`
}

function repoLabel(host: string): string {
    if (host === 'github') return 'GitHub'
    if (host === 'gitlab') return 'GitLab'
    return 'Repo'
}
</script>

<template>
    <FilterBar
        v-model:query="query"
        v-model:typeSel="typeSel"
        v-model:implSel="implSel"
        v-model:targetSel="targetSel"
        v-model:artifactSel="artifactSel"
        v-model:maturitySel="maturitySel"
        v-model:statusSel="statusSel"
        v-model:sortBy="sortBy"
        :taxonomy="data.taxonomy"
    />

    <div class="project-count" aria-live="polite" aria-atomic="true">
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

        <template v-if="filtered.length > 0">
            <div v-for="p in filtered" :key="p.id" class="project-row">
                <div class="col-name">
                    <div class="project-name">{{ p.name }}</div>
                    <div v-if="p.notes" class="project-notes">{{ p.notes }}</div>
                    <div class="project-badges">
                        <span v-for="t in p.tags?.slice(0, 4)" :key="t" class="tag">{{ t }}</span>
                        <span v-if="(p.tags?.length ?? 0) > 4" class="tag-more">+{{ (p.tags?.length ?? 0) - 4 }}</span>
                        <span v-for="a in p.artifact" :key="a" class="artifact-badge">{{ a }}</span>
                    </div>
                </div>

                <div class="col-type">
                    <span class="type-badge">{{ p.type }}</span>
                </div>

                <div class="col-impl">
                    <div class="impl-list">
                        <span v-for="impl in p.implementation" :key="impl" class="impl-item">{{ impl }}</span>
                    </div>
                    <div v-if="p.derived?.primary_language" class="primary-lang">{{ p.derived.primary_language }}</div>
                </div>

                <div class="col-target">
                    <div class="target-list">
                        <span v-for="target in p.target?.slice(0, 3)" :key="target" class="target-item">{{ target }}</span>
                        <span v-if="(p.target?.length ?? 0) > 3" class="target-more">+{{ (p.target?.length ?? 0) - 3 }}</span>
                    </div>
                </div>

                <div class="col-status">
                    <div class="status-info">
                        <div class="status-row">
                            <span class="status-label">Maturity</span>
                            <span class="maturity">{{ p.maturity || '—' }}</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">Status</span>
                            <span class="status">{{ p.status || '—' }}</span>
                        </div>
                        <div v-if="p.derived?.last_commit" class="status-row">
                            <span class="status-label">Commit</span>
                            <span class="last-commit">{{ relativeTime(p.derived.last_commit) }}</span>
                        </div>
                    </div>
                </div>

                <div class="col-links">
                    <div class="link-buttons">
                        <a
                            v-for="repo in p.repos" :key="repo.url"
                            :href="repo.url" target="_blank" rel="noopener"
                            class="link-btn repo"
                            :aria-label="`${repoLabel(repo.host)} repository for ${p.name}`"
                        >{{ repoLabel(repo.host) }}</a>
                        <a
                            v-if="p.links?.site"
                            :href="p.links.site" target="_blank" rel="noopener"
                            class="link-btn site"
                            :aria-label="`Site for ${p.name}`"
                        >Site</a>
                        <a
                            v-if="p.links?.docs"
                            :href="p.links.docs" target="_blank" rel="noopener"
                            class="link-btn docs"
                            :aria-label="`Docs for ${p.name}`"
                        >Docs</a>
                        <a
                            v-if="p.links?.issues"
                            :href="p.links.issues" target="_blank" rel="noopener"
                            class="link-btn issues"
                            :aria-label="`Issues for ${p.name}`"
                        >Issues</a>
                    </div>
                    <div v-if="p.derived?.stars" class="star-count">★ {{ p.derived.stars }}</div>
                </div>
            </div>
        </template>

        <div v-else class="empty-state">
            No projects match the current filters.
        </div>
    </div>
</template>

<style src="./ProjectList.css" scoped />
