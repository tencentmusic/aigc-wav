# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 9:10:22 2025

"""
import os
import sys
import struct


def insert_aigc_chunk(input_wav, output_wav, aigc_data):
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_wav):
            raise FileNotFoundError(f"输入文件 {input_wav} 不存在")
        
        # 检查输出文件路径是否可写
        output_dir = os.path.dirname(output_wav) or '.'
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"输出目录 {output_dir} 不可写")
        
        with open(input_wav, 'rb') as f:
            riff = f.read(12)  # 0-11: RIFF header(4), size(4), WAVE(4)
            chunks = []

            while True:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break
                chunk_id, chunk_size = struct.unpack('<4sI', chunk_header)
                chunk_data = f.read(chunk_size)
                # 奇数长度补齐
                if chunk_size % 2 == 1:
                    chunk_data += f.read(1)
                chunks.append((chunk_id, chunk_size, chunk_data))

        # 准备AIGC chunk
        aigc_id = b'AIGC'
        aigc_size = len(aigc_data)
        # 奇数长度补齐
        if aigc_size % 2 == 1:
            aigc_data += b'\x00'
        aigc_chunk = (aigc_id, aigc_size, aigc_data)

        # 构建输出：RIFF头 + fmt + AIGC + 其他chunks
        new_chunks = []
        inserted = False
        for chunk in chunks:
            new_chunks.append(chunk)
            # 在fmt后插入AIGC
            if chunk[0] == b'fmt ' and not inserted:
                new_chunks.append(aigc_chunk)
                inserted = True

        # 计算新的RIFF size
        riff_size = 4  # "WAVE"
        for chunk in new_chunks:
            l = chunk[1]
            # 每块头8字节+数据长度，若数据长度为奇数加1
            riff_size += 8 + l
            if l % 2 == 1:
                riff_size += 1

        # 写入新文件
        with open(output_wav, 'wb') as f:
            # RIFF头
            f.write(b'RIFF')
            f.write(struct.pack('<I', riff_size))
            f.write(b'WAVE')
            # 写入chunks
            for chunk_id, chunk_size, chunk_data in new_chunks:
                f.write(chunk_id)
                f.write(struct.pack('<I', chunk_size))
                if isinstance(chunk_data, str):
                    chunk_data = chunk_data.encode('utf-8')
                f.write(chunk_data)
    except Exception as e:
        print(f"处理文件时发生错误: {e}", file=sys.stderr)
        raise
            
            
def demo():
    # 示例用法
    aigc_json = '{"Label":"value1","ContentProducer":"value2","ProduceID":"value3","ReservedCode1":"value4","ContentPropagator":"value5","PropagateID":"value6","ReservedCode2":"value7"}'
    try:
        insert_aigc_chunk(
            input_wav='sample.wav',
            output_wav='sample_aigc_tag.wav',
            aigc_data=aigc_json
        )
        print("AIGC字段已写入sample_aigc_tag.wav")
    except Exception as e:
        print(f"示例运行失败: {e}", file=sys.stderr)
    
    
if __name__ == "__main__":
    demo()
    
    