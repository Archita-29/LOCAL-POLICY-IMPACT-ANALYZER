import sys
import os
import datetime

# Add the backend to sys.path to access models
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.core.database import SessionLocal
from app.models.models import Scheme, Mention
from local_policy_scraper.items import SchemeItem, MentionItem

class SQLAlchemyPipeline:
    def __init__(self):
        self.db = None

    def open_spider(self, spider):
        self.db = SessionLocal()

    def close_spider(self, spider):
        if self.db:
            self.db.close()

    def process_item(self, item, spider):
        if isinstance(item, SchemeItem):
            # Check if scheme exists
            scheme = self.db.query(Scheme).filter(Scheme.name == item.get('name')).first()
            if not scheme:
                scheme = Scheme(
                    name=item.get('name'),
                    launching_authority=item.get('launching_authority', 'Maharashtra Government'),
                    category=item.get('category'),
                    launch_date=item.get('launch_date'),
                    target_beneficiaries=item.get('target_beneficiaries'),
                    budget_allocated=item.get('budget_allocated'),
                    description=item.get('description'),
                    source_url=item.get('source_url')
                )
                self.db.add(scheme)
                self.db.commit()
            
        elif isinstance(item, MentionItem):
            # Find the scheme
            scheme = self.db.query(Scheme).filter(Scheme.name == item.get('scheme_name')).first()
            if scheme:
                # Basic dedup by URL and raw_text
                existing = self.db.query(Mention).filter(
                    Mention.scheme_id == scheme.id, 
                    Mention.url == item.get('url')
                ).first()
                
                if not existing:
                    mention = Mention(
                        scheme_id=scheme.id,
                        source=item.get('source'),
                        raw_text=item.get('raw_text'),
                        language=item.get('language', 'hi'),
                        published_date=item.get('published_date', datetime.datetime.utcnow()),
                        url=item.get('url')
                    )
                    self.db.add(mention)
                    self.db.commit()
        return item
