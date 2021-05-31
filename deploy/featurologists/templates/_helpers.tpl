{{/*
Expand the name of the chart.
*/}}
{{- define "featurologists.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
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
    secretName: {{ required ".Values.git.deployKeySecret.name is required!" .Values.git.deployKeySecret.name }}
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
    mountPath: /project
  - name: ssh-secret-volume
    mountPath: /etc/ssh
  env:
  - name: GIT_SSH_COMMAND
    value: 'ssh -i /etc/ssh/id_rsa -o "StrictHostKeyChecking=no"'
  - name: GIT_REPO
    value: {{ required ".Values.git.repo is required!" .Values.git.repo }}
  - name: GIT_REVISION
    value: {{ required ".Values.git.revision is required!" .Values.git.revision }}
  command:
  - sh
  - -x
  - -c
  - >-
    true
    && git clone "${GIT_REPO}" /project
    && cd /project
    && git reset --hard "${GIT_REVISION}"
{{- end }}
