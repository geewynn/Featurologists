{{/*
Expand the name of the chart.
*/}}
{{- define "featurologists.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "featurologists.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "featurologists.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "featurologists.labels" -}}
helm.sh/chart: {{ include "featurologists.chart" . }}
{{ include "featurologists.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "featurologists.selectorLabels" -}}
app.kubernetes.io/name: {{ include "featurologists.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "featurologists.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "featurologists.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Git repo volume name
*/}}
{{- define "gitClone.volumeName" -}}
git-repo
{{- end }}

{{/*
Volumes to clone git repo
*/}}
{{- define "gitClone.volumes" -}}
- name: {{ include "gitClone.volumeName" . }}
  emptyDir: {}
- name: ssh-secret-volume
  secret:
    secretName: {{ template "ofzinference.fullname" . }}-github
    items:
    - key: id_rsa
      path: id_rsa
      mode: 0600
{{- end }}

{{/*
Init container to clone git repo
*/}}
{{- define "gitClone.initContainer" -}}
- image: alpine/git:1.0.27
  name: git-clone
  volumeMounts:
  - name: {{ include "gitClone.volumeName" . }}
    mountPath: /tmp/git
  - name: ssh-secret-volume
    mountPath: /etc/ssh
  env:
  - name: GIT_SSH_COMMAND
    value: 'ssh -i /etc/ssh/id_rsa -o "StrictHostKeyChecking=no"'
  command:
  - git
  - clone
  - {{ .Values.git.repo | required }}
  - -b
  - {{ .Values.git.branch | required }}
  - /tmp/git
{{- end }}
