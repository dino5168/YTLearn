import sys
import os

# 添加專案根目錄到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from lib_db.models.Subtitle import Subtitle
from lib_db.schemas.Subtitle import SubtitleCreate, SubtitleUpdate


def create_subtitle(db: Session, subtitle: SubtitleCreate) -> Subtitle:
    """Create a new subtitle record in the database."""
    try:
        # 對於 Pydantic v1 使用 dict()，v2 使用 model_dump()
        try:
            subtitle_data = subtitle.model_dump()
        except AttributeError:
            subtitle_data = subtitle.dict()

        db_subtitle = Subtitle(**subtitle_data)
        db.add(db_subtitle)
        db.commit()
        db.refresh(db_subtitle)
        return db_subtitle
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def get_subtitle(db: Session, subtitle_id: int) -> Subtitle | None:
    """Get a subtitle by its ID."""
    return db.query(Subtitle).filter(Subtitle.id == subtitle_id).first()


def get_subtitles_by_video(db: Session, video_id: str) -> list[Subtitle]:
    """Get all subtitles for a specific video, ordered by sequence number."""
    return (
        db.query(Subtitle)
        .filter(Subtitle.video_id == video_id)
        .order_by(Subtitle.seq)
        .all()
    )


def update_subtitle(
    db: Session, subtitle_id: int, subtitle_update: SubtitleUpdate
) -> Subtitle | None:
    """Update an existing subtitle record."""
    print(f"尝试更新 subtitle_id: {subtitle_id}")

    # 1. 使用更明确的查询，确保只查询不创建
    db_subtitle = db.query(Subtitle).filter(Subtitle.id == subtitle_id).first()
    print(f"查询结果: {db_subtitle}")
    print(f"db_subtitle 是不是 None？ {db_subtitle is None}")

    # 2. 如果记录不存在，直接返回 None
    if db_subtitle is None:
        print(f"未找到 ID 为 {subtitle_id} 的字幕记录")
        return None

    # 3. 记录更新前的状态
    print(f"更新前的记录 ID: {db_subtitle.id}")

    try:
        # 获取更新数据
        try:
            update_data = subtitle_update.model_dump(exclude_unset=True)
        except AttributeError:
            update_data = subtitle_update.dict(exclude_unset=True)

        # 4. 确保不会更新主键
        if "id" in update_data:
            print("警告: 尝试更新主键，已移除")
            update_data.pop("id")

        if not update_data:
            print("没有需要更新的字段")
            return db_subtitle

        # 列出使用者实际上传了哪些字段和值
        print("使用者上传的更新资料:")
        for key, val in update_data.items():
            print(f"  {key}: {val}")

        # 5. 逐个更新字段
        for field, value in update_data.items():
            if hasattr(db_subtitle, field):
                old_value = getattr(db_subtitle, field)
                setattr(db_subtitle, field, value)
                print(f"更新字段 {field}: {old_value} -> {value}")
            else:
                print(f"警告: 字段 {field} 不存在于模型中")

        # 6. 提交前再次确认记录存在
        db.flush()  # 先 flush 到数据库但不提交

        # 验证记录仍然存在且是同一个
        check_subtitle = db.query(Subtitle).filter(Subtitle.id == subtitle_id).first()
        if check_subtitle is None or check_subtitle.id != db_subtitle.id:
            print("错误: 更新过程中记录发生了变化")
            db.rollback()
            return None

        db.commit()
        db.refresh(db_subtitle)
        print(f"成功更新记录，ID: {db_subtitle.id}")
        return db_subtitle

    except SQLAlchemyError as e:
        print(f"更新失败: {str(e)}")
        db.rollback()
        raise e


def update_subtitle_by_video_seq(
    db: Session, video_id: str, seq: int, subtitle_update: SubtitleUpdate
) -> Subtitle | None:
    """根据 video_id 和 seq 更新字幕记录"""
    print(f"尝试更新 video_id: {video_id}, seq: {seq}")

    # 使用复合条件查询
    db_subtitle = (
        db.query(Subtitle)
        .filter(Subtitle.video_id == video_id, Subtitle.seq == seq)
        .first()
    )

    print(f"查询结果: {db_subtitle}")
    print(f"db_subtitle 是不是 None？ {db_subtitle is None}")

    if db_subtitle is None:
        print(f"未找到 video_id={video_id}, seq={seq} 的字幕记录")
        return None

    print(f"找到记录 ID: {db_subtitle.id}")

    try:
        # 获取更新数据
        try:
            update_data = subtitle_update.model_dump(exclude_unset=True)
        except AttributeError:
            update_data = subtitle_update.dict(exclude_unset=True)

        # 移除不应该更新的字段（如果你不想允许更改 video_id 和 seq）
        # update_data.pop('video_id', None)
        # update_data.pop('seq', None)
        update_data.pop("id", None)  # 确保不更新主键

        if not update_data:
            print("没有需要更新的字段")
            return db_subtitle

        print("使用者上传的更新资料:")
        for key, val in update_data.items():
            print(f"  {key}: {val}")

        # 更新字段
        for field, value in update_data.items():
            if hasattr(db_subtitle, field):
                old_value = getattr(db_subtitle, field)
                setattr(db_subtitle, field, value)
                print(f"更新字段 {field}: {old_value} -> {value}")
            else:
                print(f"警告: 字段 {field} 不存在于模型中")

        db.commit()
        db.refresh(db_subtitle)
        print(f"成功更新记录，ID: {db_subtitle.id}")
        return db_subtitle

    except SQLAlchemyError as e:
        print(f"更新失败: {str(e)}")
        db.rollback()
        raise e


# 如果你想要从请求体中提取 video_id 和 seq
def update_subtitle_from_body(
    db: Session, subtitle_update: SubtitleUpdate
) -> Subtitle | None:
    """从更新数据中提取 video_id 和 seq 进行更新"""

    # 提取查询条件
    try:
        update_dict = subtitle_update.model_dump(exclude_unset=True)
    except AttributeError:
        update_dict = subtitle_update.dict(exclude_unset=True)

    video_id = update_dict.get("video_id")
    seq = update_dict.get("seq")

    if not video_id or seq is None:
        raise ValueError("video_id 和 seq 是必需的字段")

    print(f"从请求体中提取: video_id={video_id}, seq={seq}")

    return update_subtitle_by_video_seq(db, video_id, seq, subtitle_update)


def delete_subtitle(db: Session, subtitle_id: int) -> bool:
    """Delete a subtitle by its ID."""
    db_subtitle = get_subtitle(db, subtitle_id)
    if not db_subtitle:
        return False

    try:
        db.delete(db_subtitle)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def bulk_create_subtitles(
    db: Session, subtitles: list[SubtitleCreate]
) -> list[Subtitle]:
    """Bulk create multiple subtitle records for better performance."""
    try:
        db_subtitles = []
        for subtitle in subtitles:
            # 對於 Pydantic v1 使用 dict()，v2 使用 model_dump()
            try:
                subtitle_data = subtitle.model_dump()
            except AttributeError:
                subtitle_data = subtitle.dict()
            db_subtitles.append(Subtitle(**subtitle_data))

        db.add_all(db_subtitles)
        db.commit()

        # Refresh all objects to get their IDs
        for db_subtitle in db_subtitles:
            db.refresh(db_subtitle)
        return db_subtitles
    except SQLAlchemyError as e:
        db.rollback()
        raise e


def delete_subtitles_by_video(db: Session, video_id: str) -> int:
    """Delete all subtitles for a specific video. Returns count of deleted records."""
    try:
        count = db.query(Subtitle).filter(Subtitle.video_id == video_id).count()
        db.query(Subtitle).filter(Subtitle.video_id == video_id).delete()
        db.commit()
        return count
    except SQLAlchemyError as e:
        db.rollback()
        raise e
