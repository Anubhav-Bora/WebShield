import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.db.models.analytics import WebhookAnalytics
from datetime import datetime, timedelta
from collections import defaultdict

    # ...existing code...
        
        result = await db.execute(stmt)
        analytics = result.scalars().all()
        
        print(f"Raw query returned: {len(analytics)} records")
        
        if not analytics:
            print("No analytics found!")
            return []
        
        # If no provider_id specified, aggregate by hour across all providers
        if not provider_id:
            aggregated = defaultdict(lambda: {
                'hour': None,
                'total_webhooks': 0,
                'successful_webhooks': 0,
                'failed_webhooks': 0,
                'pending_webhooks': 0,
                'success_rate': 0.0,
                'avg_latency_ms': 0.0,
                'p50_latency_ms': 0.0,
                'p95_latency_ms': 0.0,
                'p99_latency_ms': 0.0,
                'count': 0
            })
            
            for a in analytics:
                hour_key = a.hour.isoformat()
                aggregated[hour_key]['hour'] = a.hour.isoformat()
                aggregated[hour_key]['total_webhooks'] += a.total_webhooks
                aggregated[hour_key]['successful_webhooks'] += a.successful_webhooks
                aggregated[hour_key]['failed_webhooks'] += a.failed_webhooks
                aggregated[hour_key]['pending_webhooks'] += a.pending_webhooks
                aggregated[hour_key]['avg_latency_ms'] += a.avg_latency_ms
                aggregated[hour_key]['p50_latency_ms'] += a.p50_latency_ms
                aggregated[hour_key]['p95_latency_ms'] += a.p95_latency_ms
                aggregated[hour_key]['p99_latency_ms'] += a.p99_latency_ms
                aggregated[hour_key]['count'] += 1
            
            result_list = []
            for hour_key in sorted(aggregated.keys()):
                data = aggregated[hour_key]
                if data['count'] > 0:
                    data['success_rate'] = (data['successful_webhooks'] / data['total_webhooks'] * 100) if data['total_webhooks'] > 0 else 0
                    data['avg_latency_ms'] /= data['count']
                    data['p50_latency_ms'] /= data['count']
                    data['p95_latency_ms'] /= data['count']
                    data['p99_latency_ms'] /= data['count']
                    result_list.append(data)
            
            print(f"After aggregation: {len(result_list)} points")
            print(f"First point: {result_list[0]}")
            print(f"Last point: {result_list[-1]}")
            
            # Simulate JSON serialization
            json_str = json.dumps(result_list)
            print(f"JSON length: {len(json_str)} bytes")
            print(f"JSON first 200 chars: {json_str[:200]}")
            
            return result_list
        
        return []

asyncio.run(test_api_logic())
