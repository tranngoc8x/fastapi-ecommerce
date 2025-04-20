# Hướng dẫn triển khai

Tài liệu này cung cấp hướng dẫn chi tiết để triển khai ứng dụng FastAPI E-commerce lên môi trường production.

## Tổng quan

Ứng dụng FastAPI E-commerce được thiết kế để triển khai dưới dạng các container Docker, sử dụng Docker Compose cho môi trường phát triển và Kubernetes cho môi trường production.

## Triển khai với Docker Compose

### Yêu cầu

- Docker và Docker Compose
- Ít nhất 4GB RAM
- 10GB dung lượng ổ đĩa trống

### Các bước triển khai

1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-ecommerce.git
   cd fastapi-ecommerce
   ```

2. Tạo file `.env` từ template:
   ```bash
   cp .env.example .env
   ```

3. Chỉnh sửa file `.env` với các thông số phù hợp:
   ```
   # Database
   POSTGRES_SERVER=db
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=app

   # Security
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Kafka
   KAFKA_BOOTSTRAP_SERVERS=kafka:9092
   KAFKA_PRODUCT_TOPIC=product-events
   KAFKA_ORDER_TOPIC=order-events
   KAFKA_USER_TOPIC=user-events
   KAFKA_TASK_TOPIC=async-tasks
   KAFKA_TASK_RESULT_TOPIC=task-results
   KAFKA_STREAM_INPUT_TOPIC=stream-input
   KAFKA_STREAM_OUTPUT_TOPIC=stream-output

   # Celery
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   ```

4. Khởi động các dịch vụ:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. Chạy migrations:
   ```bash
   docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
   ```

6. Tạo user admin đầu tiên:
   ```bash
   docker-compose -f docker-compose.prod.yml exec api python -m app.initial_data
   ```

7. Kiểm tra logs:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

8. API sẽ có sẵn tại: http://localhost:8000

## Triển khai với Kubernetes

### Yêu cầu

- Kubernetes cluster (minikube, GKE, EKS, AKS, etc.)
- kubectl
- helm

### Các bước triển khai

1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/fastapi-ecommerce.git
   cd fastapi-ecommerce
   ```

2. Tạo namespace:
   ```bash
   kubectl create namespace fastapi-ecommerce
   ```

3. Tạo ConfigMap và Secret:
   ```bash
   # ConfigMap
   kubectl create configmap app-config \
     --from-literal=POSTGRES_SERVER=postgres \
     --from-literal=POSTGRES_USER=postgres \
     --from-literal=POSTGRES_DB=app \
     --from-literal=KAFKA_BOOTSTRAP_SERVERS=kafka:9092 \
     --from-literal=KAFKA_PRODUCT_TOPIC=product-events \
     --from-literal=KAFKA_ORDER_TOPIC=order-events \
     --from-literal=KAFKA_USER_TOPIC=user-events \
     --from-literal=KAFKA_TASK_TOPIC=async-tasks \
     --from-literal=KAFKA_TASK_RESULT_TOPIC=task-results \
     --from-literal=KAFKA_STREAM_INPUT_TOPIC=stream-input \
     --from-literal=KAFKA_STREAM_OUTPUT_TOPIC=stream-output \
     --from-literal=CELERY_BROKER_URL=redis://redis:6379/0 \
     --from-literal=CELERY_RESULT_BACKEND=redis://redis:6379/0 \
     -n fastapi-ecommerce

   # Secret
   kubectl create secret generic app-secret \
     --from-literal=POSTGRES_PASSWORD=postgres \
     --from-literal=SECRET_KEY=your-secret-key \
     --from-literal=ALGORITHM=HS256 \
     --from-literal=ACCESS_TOKEN_EXPIRE_MINUTES=30 \
     -n fastapi-ecommerce
   ```

4. Triển khai PostgreSQL:
   ```bash
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm install postgres bitnami/postgresql \
     --set postgresqlUsername=postgres \
     --set postgresqlPassword=postgres \
     --set postgresqlDatabase=app \
     -n fastapi-ecommerce
   ```

5. Triển khai Redis:
   ```bash
   helm install redis bitnami/redis \
     --set auth.enabled=false \
     -n fastapi-ecommerce
   ```

6. Triển khai Kafka:
   ```bash
   helm install kafka bitnami/kafka \
     --set replicaCount=3 \
     --set autoCreateTopicsEnable=true \
     -n fastapi-ecommerce
   ```

7. Triển khai ứng dụng:
   ```bash
   kubectl apply -f kubernetes/api.yaml -n fastapi-ecommerce
   kubectl apply -f kubernetes/celery-worker.yaml -n fastapi-ecommerce
   kubectl apply -f kubernetes/kafka-consumer.yaml -n fastapi-ecommerce
   ```

8. Triển khai Ingress:
   ```bash
   kubectl apply -f kubernetes/ingress.yaml -n fastapi-ecommerce
   ```

9. Chạy migrations:
   ```bash
   kubectl exec -it $(kubectl get pod -l app=api -n fastapi-ecommerce -o jsonpath="{.items[0].metadata.name}") -n fastapi-ecommerce -- alembic upgrade head
   ```

10. Tạo user admin đầu tiên:
    ```bash
    kubectl exec -it $(kubectl get pod -l app=api -n fastapi-ecommerce -o jsonpath="{.items[0].metadata.name}") -n fastapi-ecommerce -- python -m app.initial_data
    ```

11. Kiểm tra logs:
    ```bash
    kubectl logs -f -l app=api -n fastapi-ecommerce
    ```

## Triển khai lên AWS

### Yêu cầu

- AWS CLI
- eksctl
- kubectl
- helm

### Các bước triển khai

1. Tạo EKS cluster:
   ```bash
   eksctl create cluster \
     --name fastapi-ecommerce \
     --version 1.21 \
     --region us-west-2 \
     --nodegroup-name standard-workers \
     --node-type t3.medium \
     --nodes 3 \
     --nodes-min 1 \
     --nodes-max 4 \
     --managed
   ```

2. Cấu hình kubectl:
   ```bash
   aws eks update-kubeconfig --name fastapi-ecommerce --region us-west-2
   ```

3. Tạo RDS PostgreSQL:
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier fastapi-ecommerce \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username postgres \
     --master-user-password postgres \
     --allocated-storage 20 \
     --db-name app
   ```

4. Tạo ElastiCache Redis:
   ```bash
   aws elasticache create-cache-cluster \
     --cache-cluster-id fastapi-ecommerce \
     --cache-node-type cache.t3.micro \
     --engine redis \
     --num-cache-nodes 1
   ```

5. Tạo MSK Kafka:
   ```bash
   aws kafka create-cluster \
     --cluster-name fastapi-ecommerce \
     --broker-node-group-info file://kafka-broker-info.json \
     --kafka-version 2.8.1 \
     --number-of-broker-nodes 3
   ```

6. Tiếp tục với các bước 2-11 từ phần "Triển khai với Kubernetes", sử dụng thông tin kết nối từ các dịch vụ AWS đã tạo.

## Triển khai lên Google Cloud

### Yêu cầu

- Google Cloud SDK
- kubectl
- helm

### Các bước triển khai

1. Tạo GKE cluster:
   ```bash
   gcloud container clusters create fastapi-ecommerce \
     --num-nodes=3 \
     --machine-type=e2-standard-2 \
     --region=us-central1
   ```

2. Cấu hình kubectl:
   ```bash
   gcloud container clusters get-credentials fastapi-ecommerce --region=us-central1
   ```

3. Tạo Cloud SQL PostgreSQL:
   ```bash
   gcloud sql instances create fastapi-ecommerce \
     --database-version=POSTGRES_13 \
     --tier=db-f1-micro \
     --region=us-central1 \
     --root-password=postgres
   
   gcloud sql databases create app --instance=fastapi-ecommerce
   ```

4. Tạo Memorystore Redis:
   ```bash
   gcloud redis instances create fastapi-ecommerce \
     --size=1 \
     --region=us-central1 \
     --redis-version=redis_6_x
   ```

5. Tiếp tục với các bước 2-11 từ phần "Triển khai với Kubernetes", sử dụng thông tin kết nối từ các dịch vụ Google Cloud đã tạo.

## Triển khai lên Azure

### Yêu cầu

- Azure CLI
- kubectl
- helm

### Các bước triển khai

1. Tạo AKS cluster:
   ```bash
   az aks create \
     --resource-group myResourceGroup \
     --name fastapi-ecommerce \
     --node-count 3 \
     --enable-addons monitoring \
     --generate-ssh-keys
   ```

2. Cấu hình kubectl:
   ```bash
   az aks get-credentials --resource-group myResourceGroup --name fastapi-ecommerce
   ```

3. Tạo Azure Database for PostgreSQL:
   ```bash
   az postgres server create \
     --name fastapi-ecommerce \
     --resource-group myResourceGroup \
     --location eastus \
     --admin-user postgres \
     --admin-password postgres \
     --sku-name GP_Gen5_2
   
   az postgres db create \
     --name app \
     --server-name fastapi-ecommerce \
     --resource-group myResourceGroup
   ```

4. Tạo Azure Cache for Redis:
   ```bash
   az redis create \
     --name fastapi-ecommerce \
     --resource-group myResourceGroup \
     --location eastus \
     --sku Basic \
     --vm-size C0
   ```

5. Tiếp tục với các bước 2-11 từ phần "Triển khai với Kubernetes", sử dụng thông tin kết nối từ các dịch vụ Azure đã tạo.

## Monitoring và Logging

### Prometheus và Grafana

1. Triển khai Prometheus và Grafana:
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus prometheus-community/kube-prometheus-stack \
     -n monitoring --create-namespace
   ```

2. Cấu hình Prometheus để scrape metrics từ ứng dụng:
   ```yaml
   # prometheus-config.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: prometheus-server-conf
     labels:
       name: prometheus-server-conf
   data:
     prometheus.yml: |-
       scrape_configs:
         - job_name: 'fastapi-ecommerce'
           scrape_interval: 5s
           static_configs:
             - targets: ['api:8000']
   ```

3. Triển khai dashboard Grafana cho FastAPI:
   ```bash
   kubectl apply -f grafana-dashboard.json -n monitoring
   ```

### ELK Stack

1. Triển khai ELK Stack:
   ```bash
   helm repo add elastic https://helm.elastic.co
   helm install elasticsearch elastic/elasticsearch -n logging --create-namespace
   helm install kibana elastic/kibana -n logging
   helm install filebeat elastic/filebeat -n logging
   ```

2. Cấu hình Filebeat để thu thập logs từ ứng dụng:
   ```yaml
   # filebeat-config.yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: filebeat-config
     labels:
       app: filebeat
   data:
     filebeat.yml: |-
       filebeat.inputs:
       - type: container
         paths:
           - /var/log/containers/api-*.log
         processors:
           - add_kubernetes_metadata:
               host: ${NODE_NAME}
               matchers:
               - logs_path:
                   logs_path: "/var/log/containers/"
       output.elasticsearch:
         hosts: ["elasticsearch:9200"]
   ```

## CI/CD Pipeline

### GitHub Actions

1. Tạo file `.github/workflows/ci.yml`:
   ```yaml
   name: CI

   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v2
       - name: Set up Python
         uses: actions/setup-python@v2
         with:
           python-version: 3.9
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install -r requirements-dev.txt
       - name: Lint with flake8
         run: |
           flake8 app tests
       - name: Type check with mypy
         run: |
           mypy app
       - name: Test with pytest
         run: |
           pytest

     build:
       needs: test
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v2
       - name: Build and push Docker image
         uses: docker/build-push-action@v2
         with:
           context: .
           push: ${{ github.event_name != 'pull_request' }}
           tags: ${{ secrets.DOCKER_HUB_USERNAME }}/fastapi-ecommerce:latest
   ```

2. Tạo file `.github/workflows/cd.yml`:
   ```yaml
   name: CD

   on:
     push:
       tags:
         - 'v*'

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v2
       - name: Set up kubectl
         uses: azure/setup-kubectl@v1
       - name: Set up kubeconfig
         run: |
           mkdir -p $HOME/.kube
           echo "${{ secrets.KUBE_CONFIG }}" > $HOME/.kube/config
       - name: Deploy to Kubernetes
         run: |
           kubectl apply -f kubernetes/api.yaml
           kubectl apply -f kubernetes/celery-worker.yaml
           kubectl apply -f kubernetes/kafka-consumer.yaml
           kubectl rollout restart deployment/api
           kubectl rollout restart deployment/celery-worker
           kubectl rollout restart deployment/kafka-consumer
   ```

## Backup và Restore

### Database Backup

1. Tạo cronjob để backup database:
   ```yaml
   # db-backup-cronjob.yaml
   apiVersion: batch/v1beta1
   kind: CronJob
   metadata:
     name: db-backup
   spec:
     schedule: "0 0 * * *"  # Mỗi ngày lúc 00:00
     jobTemplate:
       spec:
         template:
           spec:
             containers:
             - name: db-backup
               image: postgres:13
               command:
               - /bin/sh
               - -c
               - |
                 pg_dump -h postgres -U postgres -d app -f /backup/app-$(date +%Y%m%d).sql
                 aws s3 cp /backup/app-$(date +%Y%m%d).sql s3://fastapi-ecommerce-backup/
               env:
               - name: PGPASSWORD
                 valueFrom:
                   secretKeyRef:
                     name: app-secret
                     key: POSTGRES_PASSWORD
               volumeMounts:
               - name: backup
                 mountPath: /backup
             volumes:
             - name: backup
               emptyDir: {}
             restartPolicy: OnFailure
   ```

### Database Restore

1. Tạo job để restore database:
   ```yaml
   # db-restore-job.yaml
   apiVersion: batch/v1
   kind: Job
   metadata:
     name: db-restore
   spec:
     template:
       spec:
         containers:
         - name: db-restore
           image: postgres:13
           command:
           - /bin/sh
           - -c
           - |
             aws s3 cp s3://fastapi-ecommerce-backup/app-20230101.sql /backup/
             psql -h postgres -U postgres -d app -f /backup/app-20230101.sql
           env:
           - name: PGPASSWORD
             valueFrom:
               secretKeyRef:
                 name: app-secret
                 key: POSTGRES_PASSWORD
           volumeMounts:
           - name: backup
             mountPath: /backup
         volumes:
         - name: backup
           emptyDir: {}
         restartPolicy: Never
   ```

## Scaling

### Horizontal Pod Autoscaler

1. Tạo HPA cho API:
   ```yaml
   # api-hpa.yaml
   apiVersion: autoscaling/v2beta2
   kind: HorizontalPodAutoscaler
   metadata:
     name: api
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: api
     minReplicas: 2
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
     - type: Resource
       resource:
         name: memory
         target:
           type: Utilization
           averageUtilization: 80
   ```

2. Tạo HPA cho Celery worker:
   ```yaml
   # celery-worker-hpa.yaml
   apiVersion: autoscaling/v2beta2
   kind: HorizontalPodAutoscaler
   metadata:
     name: celery-worker
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: celery-worker
     minReplicas: 2
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
     - type: Resource
       resource:
         name: memory
         target:
           type: Utilization
           averageUtilization: 80
   ```

## Security

### Network Policies

1. Tạo Network Policy để hạn chế traffic:
   ```yaml
   # network-policy.yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: api-network-policy
   spec:
     podSelector:
       matchLabels:
         app: api
     policyTypes:
     - Ingress
     - Egress
     ingress:
     - from:
       - podSelector:
           matchLabels:
             app: ingress-nginx
       ports:
       - protocol: TCP
         port: 8000
     egress:
     - to:
       - podSelector:
           matchLabels:
             app: postgres
       ports:
       - protocol: TCP
         port: 5432
     - to:
       - podSelector:
           matchLabels:
             app: redis
       ports:
       - protocol: TCP
         port: 6379
     - to:
       - podSelector:
           matchLabels:
             app: kafka
       ports:
       - protocol: TCP
         port: 9092
   ```

### Secret Management

1. Sử dụng Kubernetes Secrets:
   ```bash
   kubectl create secret generic app-secret \
     --from-literal=POSTGRES_PASSWORD=postgres \
     --from-literal=SECRET_KEY=your-secret-key \
     -n fastapi-ecommerce
   ```

2. Sử dụng HashiCorp Vault:
   ```bash
   helm repo add hashicorp https://helm.releases.hashicorp.com
   helm install vault hashicorp/vault \
     -n vault --create-namespace
   ```

3. Cấu hình Vault để lưu trữ secrets:
   ```bash
   kubectl exec -it vault-0 -n vault -- vault operator init
   kubectl exec -it vault-0 -n vault -- vault operator unseal
   kubectl exec -it vault-0 -n vault -- vault login
   kubectl exec -it vault-0 -n vault -- vault secrets enable -path=fastapi-ecommerce kv-v2
   kubectl exec -it vault-0 -n vault -- vault kv put fastapi-ecommerce/app \
     POSTGRES_PASSWORD=postgres \
     SECRET_KEY=your-secret-key
   ```

## Troubleshooting

### Kiểm tra logs

```bash
# API logs
kubectl logs -f -l app=api -n fastapi-ecommerce

# Celery worker logs
kubectl logs -f -l app=celery-worker -n fastapi-ecommerce

# Kafka consumer logs
kubectl logs -f -l app=kafka-consumer -n fastapi-ecommerce

# PostgreSQL logs
kubectl logs -f -l app=postgres -n fastapi-ecommerce

# Redis logs
kubectl logs -f -l app=redis -n fastapi-ecommerce

# Kafka logs
kubectl logs -f -l app=kafka -n fastapi-ecommerce
```

### Kiểm tra pod status

```bash
kubectl get pods -n fastapi-ecommerce
```

### Kiểm tra service status

```bash
kubectl get services -n fastapi-ecommerce
```

### Kiểm tra ingress status

```bash
kubectl get ingress -n fastapi-ecommerce
```

### Kiểm tra deployment status

```bash
kubectl get deployments -n fastapi-ecommerce
```

### Kiểm tra configmap và secret

```bash
kubectl get configmap -n fastapi-ecommerce
kubectl get secret -n fastapi-ecommerce
```

### Kiểm tra HPA status

```bash
kubectl get hpa -n fastapi-ecommerce
```

### Kiểm tra network policy

```bash
kubectl get networkpolicy -n fastapi-ecommerce
```

### Kiểm tra PVC status

```bash
kubectl get pvc -n fastapi-ecommerce
```

### Kiểm tra node status

```bash
kubectl get nodes
```

### Kiểm tra cluster status

```bash
kubectl cluster-info
```

### Kiểm tra resource usage

```bash
kubectl top nodes
kubectl top pods -n fastapi-ecommerce
```

### Kiểm tra events

```bash
kubectl get events -n fastapi-ecommerce
```

### Kiểm tra logs với Kibana

1. Port-forward Kibana:
   ```bash
   kubectl port-forward svc/kibana-kibana 5601:5601 -n logging
   ```

2. Truy cập Kibana tại http://localhost:5601

### Kiểm tra metrics với Grafana

1. Port-forward Grafana:
   ```bash
   kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
   ```

2. Truy cập Grafana tại http://localhost:3000
