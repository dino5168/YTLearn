from datetime import timedelta


class CUtilTime:
    @staticmethod
    def srt_time_to_seconds(t: str) -> float:
        """
        將 SRT 時間格式 '00:01:02,345' 轉為秒數（float）
        """
        hours, minutes, seconds_ms = t.split(":")
        seconds, ms = seconds_ms.split(",")
        total_seconds = (
            int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(ms) / 1000
        )
        return total_seconds

    @staticmethod
    def seconds_to_srt_time(seconds: float) -> str:
        """
        將秒數（float）轉為 SRT 時間格式 'HH:MM:SS,mmm'
        """
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        ms = int((td.total_seconds() - total_seconds) * 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"

    @staticmethod
    def time_string_to_object(t: str) -> dict:
        """
        將時間字串 '00:01:02,345' 轉為物件格式
        """
        hours, minutes, seconds_ms = t.split(":")
        seconds, ms = seconds_ms.split(",")
        return {
            "hours": int(hours),
            "minutes": int(minutes),
            "seconds": int(seconds),
            "milliseconds": int(ms),
        }

    @staticmethod
    def time_object_to_string(time_obj: dict) -> str:
        """
        將時間物件轉為時間字串 '00:01:02,345'
        """
        return "{:02}:{:02}:{:02},{:03}".format(
            time_obj.get("hours", 0),
            time_obj.get("minutes", 0),
            time_obj.get("seconds", 0),
            time_obj.get("milliseconds", 0),
        )
