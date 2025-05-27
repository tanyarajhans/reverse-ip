# Reverse-IP-Service

A simple web application that:

* Receives a client request and extracts the origin public IP.
* Reverses the IP octets (e.g., `1.2.3.4` → `4.3.2.1`).
* Stores the reversed IP in a PostgreSQL database.
* Runs in Docker, deployable via Helm to Kubernetes.
* CI/CD pipeline (GitHub Actions) builds the Docker image, pushes to Docker Hub, and deploys to GKE.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Repository Structure](#repository-structure)
3. [Database Setup (Cloud SQL)](#database-setup-cloud-sql)
4. [Local Development](#local-development)
5. [Docker](#docker)
6. [Helm Chart](#charts)
7. [Local Kubernetes with Kind](#local-kubernetes-with-kind)
8. [GKE Deployment](#gke-deployment)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Testing & Verification](#testing--verification)
11. [Cleanup](#cleanup)
12. [Next Steps](#next-steps)

---

## Prerequisites

* **Git**
* **Docker** (Desktop or Engine)
* **Helm** (v3+)
* **kubectl**
* **Google Cloud SDK** (`gcloud`)
* **Kind** (for local cluster)
* **Python 3.12+** (for local run)

---

## Repository Structure

```
reverse-ip-service/
├── app/
│   ├── app.py              # Flask application
│   └── requirements.txt    # Python dependencies
├── sql/
│   └── schema.sql          # DB schema (reverse_ips table)
├── Dockerfile              # Container build
├── .dockerignore
├── charts/
│   ├── Chart.yaml
│   ├── values.yaml         # Chart values (image, service, env hosts)
│   └── templates/
│       ├── deployment.yaml # Deployment with imagePullSecrets & env
│       ├── service.yaml    # LoadBalancer service
├── .github/
│   └── workflows/deploy.yml # CI/CD workflow
└── README.md               # This file
```

---

## Database Setup (Cloud SQL)

1. **Create a PostgreSQL instance** in GCP Cloud SQL:

   ```bash
   gcloud sql instances create reverse-ip-postgres \
     --database-version=POSTGRES_14 \
     --region=us-central1
   ```
2. **Set root password** during creation or via:

   ```bash
   gcloud sql users set-password postgres --instance=reverse-ip-postgres --password=<YOUR_DB_PASS>
   ```
3. **Create application database**:

   ```bash
   gcloud sql databases create reverseip --instance=reverse-ip-postgres
   ```
4. **Create a dedicated DB user**:

   ```bash
   gcloud sql users create reverseuser \
     --instance=reverse-ip-postgres \
     --password=<YOUR_DB_PASS>
   ```
5. **Allow connections** (add your network/public IP or use Cloud SQL Proxy).
6. **Initialize schema**:

   ```bash
   psql "host=<PUBLIC_IP> user=reverseuser dbname=reverseip password=<YOUR_DB_PASS>" -f sql/schema.sql
   ```

---

## Local Development

1. **Clone the repo**:

   ```bash
   git clone https://github.com/tanyarajhans/reverse-ip.git
   cd reverse-ip/app
   ```
2. **(Optional) Create a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Set env variables**:

   ```bash
   export DB_HOST=localhost
   export DB_NAME=reverseip
   export DB_USER=postgres
   export DB_PASS=yourpassword
   ```
5. **Run the app**:

   ```bash
   python app.py
   ```
6. **Test**:

   ```bash
   curl http://localhost:5000
   ```

---

## Docker

1. **Build the image**:

   ```bash
   docker build -t reverse-ip-app .
   ```
2. **Run a local Postgres container**:

   ```bash
   docker run --name pg -e POSTGRES_DB=reverseip \
     -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password \
     -p 5432:5432 -d postgres
   ```
3. **Run the app container**:

   ```bash
   docker run --network host \
     -e DB_HOST=127.0.0.1 -e DB_NAME=reverseip \
     -e DB_USER=postgres -e DB_PASS=password \
     -p 5000:5000 reverse-ip-app
   ```

---

## Helm Chart

1. **Configure values** in `charts/values.yaml` (omit `DB_PASS`).
2. **Create DB secret** in cluster:

   ```bash
   kubectl create secret generic db-secret --from-literal=DB_PASS=<YOUR_DB_PASS>
   ```
3. **Dry-run** render:

   ```bash
   helm lint charts
   helm install reverse-ip charts --dry-run --debug
   ```

---

## Local Kubernetes with Kind

1. **Create cluster**:

   ```bash
   kind create cluster --name reverse-ip
   ```
2. **Switch context**:

   ```bash
   kubectl cluster-info --context kind-reverse-ip
   ```
3. **Create DB secret** & **install**:

   ```bash
   kubectl create secret generic db-secret --from-literal=DB_PASS=password
   helm install reverse-ip charts
   ```
4. **Port-forward service**:

   ```bash
   kubectl port-forward svc/reverse-ip-service 8080:80
   curl http://localhost:8080
   ```
5. **Tear down**:

   ```bash
   kind delete cluster --name reverse-ip
   ```

---

## GKE Deployment

1. **Authenticate**:

   ```bash
   gcloud container clusters get-credentials my-cluster \
     --zone us-central1 --project my-gcp-project
   ```
2. **Create DB secret** as above.
3. **Install/upgrade** Helm release:

   ```bash
   helm upgrade --install reverse-ip charts
   ```
4. **Get public IP**:

   ```bash
   kubectl get svc reverse-ip-service
   ```
5. **Access**:

   ```bash
   curl http://<EXTERNAL_IP>
   ```

---

## CI/CD Pipeline

* **GitHub Actions** located at `.github/workflows/deploy.yml`.
* **Secrets**: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `GCP_CREDENTIALS`.
* **Steps**:

  1. Checkout code
  2. Build & push Docker image
  3. Authenticate to GCP & set kube context
  4. Deploy Helm chart
  5. Wait & print `http://<EXTERNAL_IP>`

---

## Testing & Verification

* Ensure **route works** with `curl`.
* Check **DB table** for inserts.
* Inspect **logs** via `kubectl logs` or GCP Cloud Logging.

---

*Created by Tanya Rajhans*
