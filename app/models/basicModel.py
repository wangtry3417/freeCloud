from . import db

class BaseModel(db.Model):
    """基礎模型類，所有模型都應繼承此類。"""
    __abstract__ = True  # 表示這是一個抽象類，不會創建表

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def create(cls, **kwargs):
        """創建新record並添加到會話中。"""
        instance = cls(**kwargs)
        db.session.add(instance)
        return instance

    @classmethod
    def get_all(cls):
        """獲取所有record。"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        """根據 ID 獲取record。"""
        return cls.query.get(id)

    @classmethod
    def delete_by_id(cls, id):
        """根據 ID 刪除record。"""
        instance = cls.get_by_id(id)
        if instance:
            db.session.delete(instance)
            return True
        return False
    @classmethod
    def _commit(cls):
      db.session.commit()
      return True
