import pygame
import sys
import random
import math
import asyncio

# 初期化
pygame.init()

# 定数定義
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# 難易度定数
DIFFICULTY_MODIFIERS = {
    "Easy":   {"hp": 1.0, "exp": 1.0, "loot_quality": 1, "color": GREEN},
    "Normal": {"hp": 1.5, "exp": 1.8, "loot_quality": 2, "color": YELLOW},
    "Hard":   {"hp": 2.0, "exp": 3.0, "loot_quality": 3, "color": RED},
}

# パワーアップ定義（通常）
POWERUP_POOL = [
    # Common（よく出る）
    {"name": "Attack Speed +10%", "type": "attack_speed", "value": 0.9, "desc": "Shoot faster", "rarity": "common"},
    {"name": "Movement Speed +10%", "type": "movement_speed", "value": 0.5, "desc": "Move faster", "rarity": "common"},
    {"name": "Max HP +10", "type": "max_hp", "value": 10, "desc": "Increase max health", "rarity": "common"},
    {"name": "Heal +20 HP", "type": "heal", "value": 20, "desc": "Restore health", "rarity": "common"},
    {"name": "Bullet Speed +30%", "type": "bullet_speed", "value": 1.3, "desc": "Faster bullets", "rarity": "common"},
    
    # Uncommon（そこそこ出る）
    {"name": "Bullet Count +1", "type": "bullet_count", "value": 1, "desc": "More bullets per shot", "rarity": "uncommon"},
    {"name": "Attack Speed +20%", "type": "attack_speed", "value": 0.8, "desc": "Shoot much faster", "rarity": "uncommon"},
    {"name": "Movement Speed +20%", "type": "movement_speed", "value": 1.0, "desc": "Move much faster", "rarity": "uncommon"},
    {"name": "Damage +1", "type": "damage", "value": 1, "desc": "Increase bullet damage", "rarity": "uncommon"},
    {"name": "Bullet Size +30%", "type": "bullet_size", "value": 1.3, "desc": "Bigger bullets, easier to hit", "rarity": "uncommon"},
    
    # Rare（レア）
    {"name": "Homing Bullets Lv1", "type": "homing", "value": 1, "desc": "Bullets slightly track enemies", "rarity": "rare"},
    {"name": "Side Cannons Lv1", "type": "side_cannon", "value": 1, "desc": "Fire bullets to the sides", "rarity": "rare"},
    {"name": "Orbital Strike", "type": "orbital", "value": 1, "desc": "Rotating shields attack nearby enemies", "rarity": "rare"},
    {"name": "Spread Shot", "type": "spread_shot", "value": 1, "desc": "Bullets spread in wider arc", "rarity": "rare"},
    {"name": "Life Steal", "type": "lifesteal", "value": 0.2, "desc": "20% chance to heal on kill", "rarity": "rare"},
    {"name": "Ally Fighter", "type": "ally", "value": 1, "desc": "Summon an ally fighter to help you", "rarity": "rare"},
    {"name": "Mine Layer", "type": "mine", "value": 1, "desc": "Leave mines where you move", "rarity": "rare"},
    
    # Epic（激レア）
    {"name": "Homing Bullets Lv2", "type": "homing", "value": 2, "desc": "Bullets moderately track enemies", "rarity": "epic"},
    {"name": "Side Cannons Lv2", "type": "side_cannon", "value": 2, "desc": "Powerful side and diagonal shots", "rarity": "epic"},
    {"name": "Homing Bullets Lv3", "type": "homing", "value": 3, "desc": "Strong homing missiles!", "rarity": "epic"},
    {"name": "Side Cannons Lv3", "type": "side_cannon", "value": 3, "desc": "Ultimate 8-way shooting!", "rarity": "epic"},
    {"name": "Ally Squadron", "type": "ally", "value": 2, "desc": "Summon 2 more ally fighters", "rarity": "epic"},
]

# 敵の種類定義
ENEMY_TYPES = {
    "normal": {
        "name": "Normal",
        "color": RED,
        "hp_mult": 1.0,
        "speed_mult": 1.0,
        "exp_mult": 1.0,
        "size": 25,
        "behavior": "straight",  # まっすぐ下に移動
    },
    "fast": {
        "name": "Fast",
        "color": (255, 100, 100),  # 明るい赤
        "hp_mult": 0.7,
        "speed_mult": 2.0,
        "exp_mult": 1.2,
        "size": 20,
        "behavior": "straight",
    },
    "tank": {
        "name": "Tank",
        "color": (150, 0, 0),  # 暗い赤
        "hp_mult": 3.0,
        "speed_mult": 0.5,
        "exp_mult": 2.0,
        "size": 35,
        "behavior": "straight",
    },
    "zigzag": {
        "name": "Zigzag",
        "color": (255, 150, 0),  # オレンジ
        "hp_mult": 1.2,
        "speed_mult": 1.0,
        "exp_mult": 1.5,
        "size": 25,
        "behavior": "zigzag",  # ジグザグ移動
    },
    "shooter": {
        "name": "Shooter",
        "color": (200, 0, 200),  # 紫
        "hp_mult": 1.5,
        "speed_mult": 0.8,
        "exp_mult": 2.5,
        "size": 28,
        "behavior": "shooter",  # より頻繁に弾を撃つ
    },
    # Epic敵（Normal/Hard難易度で出現）
    "elite": {
        "name": "Elite",
        "color": (255, 215, 0),  # 金色
        "hp_mult": 8.0,  # 4.0から8.0に強化
        "speed_mult": 1.2,
        "exp_mult": 8.0,  # 4.0から8.0に強化
        "size": 40,  # 32から40に大型化
        "behavior": "elite",  # 高速移動+射撃
    },
    "berserker": {
        "name": "Berserker",
        "color": (255, 50, 50),  # 明るい赤
        "hp_mult": 10.0,  # 5.0から10.0に強化
        "speed_mult": 1.8,  # 1.5から1.8に高速化
        "exp_mult": 10.0,  # 5.0から10.0に強化
        "size": 45,  # 40から45に大型化
        "behavior": "berserker",  # 高速突進
    },
    "sniper": {
        "name": "Sniper",
        "color": (0, 255, 255),  # シアン
        "hp_mult": 6.0,  # 2.5から6.0に強化
        "speed_mult": 0.6,
        "exp_mult": 9.0,  # 4.5から9.0に強化
        "size": 35,  # 30から35に大型化
        "behavior": "sniper",  # 精密射撃（速い弾）
    },
}

# ボス報酬専用プール（通常より強力）
# ボス報酬専用プール（通常より強力）
BOSS_REWARD_POOL = [
    {"name": "Attack Speed +50%", "type": "attack_speed", "value": 0.5, "desc": "ULTRA RAPID FIRE!", "rarity": "boss"},
    {"name": "Bullet Count +3", "type": "bullet_count", "value": 3, "desc": "Triple shot upgrade!", "rarity": "boss"},
    {"name": "Movement Speed +50%", "type": "movement_speed", "value": 2.5, "desc": "Lightning speed!", "rarity": "boss"},
    {"name": "Max HP +30", "type": "max_hp", "value": 30, "desc": "Greatly increase vitality", "rarity": "boss"},
    {"name": "Full Heal", "type": "heal", "value": 999, "desc": "Restore all HP", "rarity": "boss"},
    {"name": "Damage +3", "type": "damage", "value": 3, "desc": "Devastating firepower!", "rarity": "boss"},
    {"name": "Piercing Bullets", "type": "piercing", "value": 1, "desc": "Bullets pierce through enemies", "rarity": "boss"},
    {"name": "Double Shot", "type": "multi_shot", "value": 2, "desc": "Fire 2 volleys at once", "rarity": "boss"},
    {"name": "Orbital Strike Lv2", "type": "orbital", "value": 2, "desc": "More orbitals + faster rotation", "rarity": "boss"},
    {"name": "Explosive Bullets", "type": "explosive", "value": 1, "desc": "Bullets explode on impact", "rarity": "boss"},
    {"name": "Shield Regeneration", "type": "shield_regen", "value": 10, "desc": "Regenerate 10 HP every 10 sec", "rarity": "boss"},
    {"name": "Ultimate Homing", "type": "homing", "value": 3, "desc": "Maximum homing power!", "rarity": "boss"},
]

# レアリティ別の色と重み
RARITY_CONFIG = {
    "common": {"color": (200, 200, 200), "weight": 50, "name": "Common"},  # グレー
    "uncommon": {"color": (100, 255, 100), "weight": 30, "name": "Uncommon"},  # 緑
    "rare": {"color": (100, 150, 255), "weight": 15, "name": "Rare"},  # 青
    "epic": {"color": (200, 100, 255), "weight": 5, "name": "Epic"},  # 紫
    "boss": {"color": (255, 200, 0), "weight": 0, "name": "LEGENDARY"},  # 金
}


class Player:
    """プレイヤークラス"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = 5  # 4から5に増加
        self.hp = 30  # 3から30に増加（10倍）
        self.max_hp = 30  # 3から30に増加（10倍）
        
        # 武器関連
        self.attack_speed = 15  # 10から15に増加（遅くなる）
        self.bullet_count = 1
        self.bullet_damage = 1
        self.shoot_timer = 0
        self.piercing = False  # 貫通弾
        self.multi_shot = 1  # 一度に発射する弾幕数
        
        # 新しい能力
        self.homing_level = 0  # ホーミングレベル（0-3）
        self.orbital_level = 0  # オービタルレベル（0-2）
        self.bullet_size = 1.0  # 弾のサイズ倍率
        self.bullet_speed_mult = 1.0  # 弾速倍率
        self.spread_shot = False  # 拡散ショット
        self.lifesteal_chance = 0  # ライフスティール確率
        self.explosive_bullets = False  # 爆発弾
        self.shield_regen = False  # シールド再生
        self.shield_regen_timer = 0  # 再生タイマー
        self.side_cannon_level = 0  # サイドキャノンレベル（0-2）
        
        # 味方機システム
        self.ally_count = 0  # 味方機の数
        self.allies = []  # 味方機のリスト
        
        # 地雷システム
        self.mine_layer = False  # 地雷を設置するか
        self.mine_timer = 0  # 地雷設置タイマー
        self.mine_interval = 20  # 地雷設置間隔（フレーム）
        
        # オービタル用
        self.orbitals = []  # オービタル弾のリスト
        self.orbital_angle = 0  # 回転角度
        
        # 成長関連
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        
        # 取得済みパワーアップを記録（type: max_valueの形式で管理）
        self.acquired_powerups = {}  # 例: {"homing": 2, "side_cannon": 1}
        
    def move(self, keys):
        """キー入力による移動"""
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        # 画面外に出ないようにする
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
    
    def move_to_mouse(self, mouse_pos):
        """マウスカーソルに向かって移動"""
        target_x, target_y = mouse_pos
        
        # プレイヤーの中心座標
        player_center_x = self.x + self.width // 2
        player_center_y = self.y + self.height // 2
        
        # マウスとの距離を計算
        dx = target_x - player_center_x
        dy = target_y - player_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 距離が一定以上ある場合のみ移動（細かい振動を防ぐ）
        if distance > 5:
            # 正規化して速度を掛ける
            if distance > 0:
                dx = dx / distance * self.speed
                dy = dy / distance * self.speed
                self.x += dx
                self.y += dy
        
        # 画面外に出ないようにする
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
    
    def shoot(self, bullets):
        """弾を発射"""
        self.shoot_timer += 1
        if self.shoot_timer >= self.attack_speed:
            self.shoot_timer = 0
            
            # 前方ショット
            # マルチショット対応
            for shot in range(self.multi_shot):
                # 弾数に応じて発射
                bullet_angles = []
                if self.spread_shot:
                    # 拡散ショット：より広い範囲に
                    for i in range(self.bullet_count):
                        angle = -30 + (60 / max(1, self.bullet_count - 1)) * i if self.bullet_count > 1 else 0
                        bullet_angles.append(angle)
                else:
                    # 通常ショット
                    bullet_angles = [0] * self.bullet_count
                
                for i in range(self.bullet_count):
                    if self.spread_shot:
                        angle = bullet_angles[i]
                        rad = math.radians(angle)
                        speed_x = math.sin(rad) * 10
                        speed_y = -math.cos(rad) * 10
                        bullets.append(Bullet(
                            self.x + self.width // 2, 
                            self.y - shot * 10,
                            speed_y,
                            self.bullet_damage,
                            self.piercing,
                            self.homing_level,
                            self.bullet_size,
                            self.bullet_speed_mult
                        ))
                        bullets[-1].speed_x = speed_x
                    else:
                        offset = (i - (self.bullet_count - 1) / 2) * 20
                        bullets.append(Bullet(
                            self.x + self.width // 2 + offset, 
                            self.y - shot * 10,
                            -10,
                            self.bullet_damage,
                            self.piercing,
                            self.homing_level,
                            self.bullet_size,
                            self.bullet_speed_mult
                        ))
            
            # サイドキャノン
            if self.side_cannon_level > 0:
                self.shoot_side_cannons(bullets)
    
    def shoot_side_cannons(self, bullets):
        """サイドキャノンから弾を発射"""
        player_center_y = self.y + self.height // 2
        
        if self.side_cannon_level == 1:
            # レベル1：左右に真横に発射
            # 左側
            bullets.append(Bullet(
                self.x,
                player_center_y,
                0,  # 上下移動なし
                self.bullet_damage,
                self.piercing,
                self.homing_level,
                self.bullet_size * 0.8,  # 少し小さめ
                self.bullet_speed_mult
            ))
            bullets[-1].speed_x = -8  # 左に発射
            
            # 右側
            bullets.append(Bullet(
                self.x + self.width,
                player_center_y,
                0,
                self.bullet_damage,
                self.piercing,
                self.homing_level,
                self.bullet_size * 0.8,
                self.bullet_speed_mult
            ))
            bullets[-1].speed_x = 8  # 右に発射
            
        elif self.side_cannon_level == 2:
            # レベル2：左右 + 斜め（合計6方向）
            directions = [
                (-8, 0),    # 左
                (8, 0),     # 右
                (-6, -6),   # 左上
                (6, -6),    # 右上
                (-6, 6),    # 左下
                (6, 6),     # 右下
            ]
            
            for speed_x, speed_y in directions:
                bullet = Bullet(
                    self.x + self.width // 2,
                    player_center_y,
                    speed_y,
                    self.bullet_damage,
                    self.piercing,
                    self.homing_level,
                    self.bullet_size * 0.7,  # さらに小さめ
                    self.bullet_speed_mult
                )
                bullet.speed_x = speed_x
                bullets.append(bullet)
                
        elif self.side_cannon_level >= 3:
            # レベル3：8方向全方位射撃
            directions = [
                (0, -8),     # 上
                (8, 0),      # 右
                (0, 8),      # 下
                (-8, 0),     # 左
                (6, -6),     # 右上
                (6, 6),      # 右下
                (-6, 6),     # 左下
                (-6, -6),    # 左上
            ]
            
            for speed_x, speed_y in directions:
                bullet = Bullet(
                    self.x + self.width // 2,
                    player_center_y,
                    speed_y,
                    self.bullet_damage,
                    self.piercing,
                    self.homing_level,
                    self.bullet_size * 0.6,  # 最も小さめ
                    self.bullet_speed_mult
                )
                bullet.speed_x = speed_x
                bullets.append(bullet)
    
    def add_exp(self, amount):
        """経験値を追加"""
        self.exp += amount
        if self.exp >= self.exp_to_next:
            return True  # レベルアップ
        return False
    
    def level_up(self):
        """レベルアップ処理"""
        self.level += 1
        self.exp = 0
        self.exp_to_next = int(self.exp_to_next * 1.5)
    
    def apply_powerup(self, powerup):
        """パワーアップを適用"""
        powerup_type = powerup["type"]
        value = powerup["value"]
        
        # heal以外は取得済みとして記録（最大値を保持）
        if powerup_type != "heal":
            # 数値系（attack_speed, movement_speed, bullet_speed, bullet_size）は累積値を記録
            if powerup_type in ["attack_speed", "movement_speed", "bullet_speed", "bullet_size"]:
                if powerup_type in self.acquired_powerups:
                    # 同じタイプの累積を防ぐため、より高い効果のもののみ記録
                    if powerup_type == "attack_speed":
                        # attack_speedは小さいほど高速（0.9, 0.8など）
                        self.acquired_powerups[powerup_type] = min(self.acquired_powerups[powerup_type], value)
                    else:
                        # その他は大きいほど高速/強力
                        self.acquired_powerups[powerup_type] = max(self.acquired_powerups[powerup_type], value)
                else:
                    self.acquired_powerups[powerup_type] = value
            else:
                # レベル制のものは最大値を記録
                if powerup_type in self.acquired_powerups:
                    self.acquired_powerups[powerup_type] = max(self.acquired_powerups[powerup_type], value)
                else:
                    self.acquired_powerups[powerup_type] = value
        
        if powerup_type == "attack_speed":
            self.attack_speed = max(1, int(self.attack_speed * value))
        elif powerup_type == "bullet_count":
            self.bullet_count += value
        elif powerup_type == "movement_speed":
            self.speed += value
        elif powerup_type == "max_hp":
            self.max_hp += value
            self.hp += value  # 最大HPが増えたら現在HPも回復
        elif powerup_type == "heal":
            self.hp = min(self.max_hp, self.hp + value)
        elif powerup_type == "damage":
            self.bullet_damage += value
        elif powerup_type == "piercing":
            self.piercing = True
        elif powerup_type == "multi_shot":
            self.multi_shot += value
        elif powerup_type == "homing":
            self.homing_level = max(self.homing_level, value)
        elif powerup_type == "orbital":
            self.orbital_level = max(self.orbital_level, value)
            self.init_orbitals()
        elif powerup_type == "bullet_size":
            self.bullet_size *= value
        elif powerup_type == "bullet_speed":
            self.bullet_speed_mult *= value
        elif powerup_type == "spread_shot":
            self.spread_shot = True
        elif powerup_type == "lifesteal":
            self.lifesteal_chance = value
        elif powerup_type == "explosive":
            self.explosive_bullets = True
        elif powerup_type == "shield_regen":
            self.shield_regen = True
        elif powerup_type == "side_cannon":
            self.side_cannon_level = max(self.side_cannon_level, value)
        elif powerup_type == "ally":
            # 味方機を追加
            self.ally_count += value
            self.init_allies()
        elif powerup_type == "mine":
            # 地雷設置能力を有効化
            self.mine_layer = True
    
    def init_orbitals(self):
        """オービタルを初期化"""
        self.orbitals = []
        orbital_count = 2 if self.orbital_level == 1 else 4
        for i in range(orbital_count):
            angle = (360 / orbital_count) * i
            self.orbitals.append({"angle": angle, "distance": 50})
    
    def init_allies(self):
        """味方機を初期化"""
        self.allies = []
        if self.ally_count >= 1:
            # 1機目：左後方
            self.allies.append(AllyFighter(self, -40, 30))
        if self.ally_count >= 2:
            # 2機目：右後方
            self.allies.append(AllyFighter(self, 40, 30))
        if self.ally_count >= 3:
            # 3機目：左後方遠く
            self.allies.append(AllyFighter(self, -60, 50))
    
    def update_orbitals(self):
        """オービタルの位置を更新"""
        if self.orbital_level > 0:
            rotation_speed = 3 if self.orbital_level == 1 else 5
            self.orbital_angle += rotation_speed
            for orbital in self.orbitals:
                orbital["angle"] = (orbital["angle"] + rotation_speed) % 360
    
    def update_shield_regen(self):
        """シールド再生を更新"""
        if self.shield_regen:
            self.shield_regen_timer += 1
            if self.shield_regen_timer >= 600:  # 10秒
                self.shield_regen_timer = 0
                if self.hp < self.max_hp:
                    self.hp += 1
    
    def save_stats(self):
        """現在の状態を保存"""
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "speed": self.speed,
            "attack_speed": self.attack_speed,
            "bullet_count": self.bullet_count,
            "bullet_damage": self.bullet_damage,
            "piercing": self.piercing,
            "multi_shot": self.multi_shot,
            "level": self.level,
            "exp": self.exp,
            "exp_to_next": self.exp_to_next,
            "homing_level": self.homing_level,
            "orbital_level": self.orbital_level,
            "bullet_size": self.bullet_size,
            "bullet_speed_mult": self.bullet_speed_mult,
            "spread_shot": self.spread_shot,
            "lifesteal_chance": self.lifesteal_chance,
            "explosive_bullets": self.explosive_bullets,
            "shield_regen": self.shield_regen,
            "side_cannon_level": self.side_cannon_level,
        }
    
    def load_stats(self, stats):
        """保存された状態を復元"""
        self.hp = stats["hp"]
        self.max_hp = stats["max_hp"]
        self.speed = stats["speed"]
        self.attack_speed = stats["attack_speed"]
        self.bullet_count = stats["bullet_count"]
        self.bullet_damage = stats["bullet_damage"]
        self.piercing = stats["piercing"]
        self.multi_shot = stats["multi_shot"]
        self.level = stats["level"]
        self.exp = stats["exp"]
        self.exp_to_next = stats["exp_to_next"]
        self.homing_level = stats.get("homing_level", 0)
        self.orbital_level = stats.get("orbital_level", 0)
        self.bullet_size = stats.get("bullet_size", 1.0)
        self.bullet_speed_mult = stats.get("bullet_speed_mult", 1.0)
        self.spread_shot = stats.get("spread_shot", False)
        self.lifesteal_chance = stats.get("lifesteal_chance", 0)
        self.explosive_bullets = stats.get("explosive_bullets", False)
        self.shield_regen = stats.get("shield_regen", False)
        self.side_cannon_level = stats.get("side_cannon_level", 0)
        
        # オービタルを再初期化
        if self.orbital_level > 0:
            self.init_orbitals()
    
    def draw(self, screen):
        """プレイヤーを描画"""
        # オービタルを先に描画（プレイヤーの下）
        if self.orbital_level > 0:
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2
            for orbital in self.orbitals:
                angle_rad = math.radians(orbital["angle"])
                orb_x = player_center_x + math.cos(angle_rad) * orbital["distance"]
                orb_y = player_center_y + math.sin(angle_rad) * orbital["distance"]
                pygame.draw.circle(screen, YELLOW, (int(orb_x), int(orb_y)), 8)
                pygame.draw.circle(screen, WHITE, (int(orb_x), int(orb_y)), 8, 2)
        
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        # 三角形の装飾（前方向を示す）
        pygame.draw.polygon(screen, WHITE, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + 15),
            (self.x + self.width, self.y + 15)
        ])


class Bullet:
    """弾クラス"""
    def __init__(self, x, y, speed_y, damage=1, piercing=False, homing_level=0, size_mult=1.0, speed_mult=1.0):
        self.x = x
        self.y = y
        self.width = int(5 * size_mult)
        self.height = int(15 * size_mult)
        self.speed_y = speed_y * speed_mult
        self.speed_x = 0  # ホーミング用
        self.damage = damage
        self.piercing = piercing  # 貫通弾
        self.homing_level = homing_level  # ホーミングレベル
        
    def update(self, enemies=None, boss=None):
        """弾の移動（ホーミング対応）"""
        # ホーミング処理
        if self.homing_level > 0:
            closest_target = None
            closest_dist = float('inf')
            
            # 通常の敵を探す
            if enemies:
                for enemy in enemies:
                    enemy_center_x = enemy.x + enemy.width // 2
                    enemy_center_y = enemy.y + enemy.height // 2
                    dx = enemy_center_x - self.x
                    dy = enemy_center_y - self.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    
                    # 検知範囲を拡大（300→400ピクセル）
                    if dist < closest_dist and dist < 400:
                        closest_dist = dist
                        closest_target = (enemy_center_x, enemy_center_y)
            
            # ボスも対象に含める
            if boss:
                boss_center_x = boss.x + boss.width // 2
                boss_center_y = boss.y + boss.height // 2
                dx = boss_center_x - self.x
                dy = boss_center_y - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                
                # ボスの検知範囲を拡大（500→600ピクセル）
                if dist < closest_dist and dist < 600:
                    closest_dist = dist
                    closest_target = (boss_center_x, boss_center_y)
            
            # ターゲットに向かって軌道修正
            if closest_target:
                target_x, target_y = closest_target
                dx = target_x - self.x
                dy = target_y - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist > 0:
                    # ホーミングレベルに応じた旋回力を強化（0.3→0.4）
                    homing_strength = 0.4 * self.homing_level
                    self.speed_x += (dx / dist) * homing_strength
                    self.speed_y += (dy / dist) * homing_strength
                    
                    # 最大速度制限を少し緩和（12→13）
                    max_speed = 13
                    current_speed = math.sqrt(self.speed_x * self.speed_x + self.speed_y * self.speed_y)
                    if current_speed > max_speed:
                        self.speed_x = (self.speed_x / current_speed) * max_speed
                        self.speed_y = (self.speed_y / current_speed) * max_speed
        
        self.x += self.speed_x
        self.y += self.speed_y
        
    def is_off_screen(self):
        """画面外判定"""
        return self.y < -self.height or self.y > SCREEN_HEIGHT or self.x < -self.width or self.x > SCREEN_WIDTH
    
    def draw(self, screen):
        """弾を描画"""
        if self.homing_level > 0:
            # ホーミング弾は赤系
            color = (255, 100, 100)
        elif self.piercing:
            color = BLUE
        else:
            color = YELLOW
        pygame.draw.rect(screen, color, (int(self.x), int(self.y), self.width, self.height))


class Enemy:
    """敵クラス"""
    def __init__(self, x, y, difficulty_mod, stage_number=1, enemy_type="normal"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.type_data = ENEMY_TYPES[enemy_type]
        
        # サイズ
        self.width = self.type_data["size"]
        self.height = self.type_data["size"]
        
        # ステージが進むほど敵の速度が上がる（より大幅に）
        base_speed = random.uniform(1, 2) + (stage_number - 1) * 0.5  # 0.3から0.5に増加
        self.speed = base_speed * self.type_data["speed_mult"]
        
        # ステージが進むほど敵のHPが大幅に上がる
        stage_hp_mult = 1 + (stage_number - 1) * 0.8  # ステージごとに80%増加
        self.base_hp = (2 + (stage_number - 1) * 2) * self.type_data["hp_mult"] * stage_hp_mult
        self.hp = int(self.base_hp * difficulty_mod["hp"])
        self.max_hp = self.hp
        
        # 経験値もステージに応じて増加
        stage_exp_mult = 1 + (stage_number - 1) * 0.5
        self.exp_value = int(15 * difficulty_mod["exp"] * self.type_data["exp_mult"] * stage_exp_mult)
        
        # 行動パターン用
        self.behavior = self.type_data["behavior"]
        self.move_timer = 0
        self.direction = 1 if random.random() > 0.5 else -1  # ジグザグ用
        self.shoot_timer = 0
        self.shoot_interval = 120  # シューター用
        
        # Epic敵専用：滞在システム
        self.is_epic = enemy_type in ["elite", "berserker", "sniper"]
        if self.is_epic:
            self.stay_duration = 900  # 600から900に延長（15秒間滞在）
            self.stay_timer = 0
            self.staying = False
            self.target_y = random.randint(100, 200)  # 滞在位置
        
    def update(self):
        """敵の移動（行動パターン別）"""
        # Epic敵の滞在処理
        if self.is_epic:
            if not self.staying:
                # 目標位置まで移動
                if self.y < self.target_y:
                    self.y += self.speed
                else:
                    self.staying = True
            else:
                # 滞在中
                self.stay_timer += 1
                # 左右にゆっくり移動
                self.x += math.sin(self.stay_timer * 0.05) * 2
                
                # 滞在時間終了
                if self.stay_timer >= self.stay_duration:
                    self.staying = False
                    self.is_epic = False  # 通常移動に切り替え
                return
        
        if self.behavior == "straight":
            # まっすぐ下に移動
            self.y += self.speed
            
        elif self.behavior == "zigzag":
            # ジグザグ移動
            self.y += self.speed
            self.move_timer += 1
            if self.move_timer > 30:
                self.direction *= -1
                self.move_timer = 0
            self.x += self.direction * 2
            
        elif self.behavior == "shooter":
            # ゆっくり下に移動
            self.y += self.speed
            
        elif self.behavior == "elite":
            # エリート：高速ジグザグ+射撃
            self.y += self.speed
            self.move_timer += 1
            if self.move_timer > 20:
                self.direction *= -1
                self.move_timer = 0
            self.x += self.direction * 3
            
        elif self.behavior == "berserker":
            # バーサーカー：高速突進
            self.y += self.speed * 1.5
            
        elif self.behavior == "sniper":
            # スナイパー：ゆっくり移動
            self.y += self.speed
    
    def shoot(self, bullets, player_x, player_y):
        """敵の攻撃（すべての敵が撃つ）"""
        self.shoot_timer += 1
        
        # 敵タイプごとに射撃間隔を設定
        shoot_intervals = {
            "normal": 180,    # 3秒
            "fast": 240,      # 4秒（速いが撃つのは遅め）
            "tank": 150,      # 2.5秒（タフで頻繁に撃つ）
            "zigzag": 200,    # 3.3秒
            "shooter": 120,   # 2秒（最も頻繁に撃つ）
            "elite": 100,     # 1.67秒（非常に頻繁）
            "berserker": 90,  # 1.5秒（超頻繁）
            "sniper": 180,    # 3秒（遅いが速い弾）
        }
        
        interval = shoot_intervals.get(self.enemy_type, 180)
        
        if self.shoot_timer >= interval:
            self.shoot_timer = 0
            
            # プレイヤーの方向を計算
            enemy_center_x = self.x + self.width // 2
            enemy_center_y = self.y + self.height // 2
            
            dx = player_x - enemy_center_x
            dy = player_y - enemy_center_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                # 敵タイプごとの弾速
                if self.enemy_type == "sniper":
                    bullet_speed = 8  # スナイパーは速い弾
                elif self.enemy_type == "elite":
                    bullet_speed = 5
                elif self.enemy_type == "berserker":
                    bullet_speed = 6
                else:
                    bullet_speed = 4
                
                # 正規化して速度を掛ける
                speed_x = (dx / distance) * bullet_speed
                speed_y = (dy / distance) * bullet_speed
                
                bullets.append(EnemyBullet(
                    enemy_center_x,
                    enemy_center_y,
                    speed_x,
                    speed_y
                ))
        
    def is_off_screen(self):
        """画面外判定"""
        return self.y > SCREEN_HEIGHT
    
    def draw(self, screen):
        """敵を描画"""
        color = self.type_data["color"]
        
        # 基本形状
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # 種類別の装飾
        if self.enemy_type == "fast":
            # 三角形で速さを表現
            pygame.draw.polygon(screen, WHITE, [
                (self.x + self.width // 2, self.y + self.height),
                (self.x, self.y),
                (self.x + self.width, self.y)
            ], 2)
        elif self.enemy_type == "tank":
            # 太い枠線でタフさを表現
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 3)
        elif self.enemy_type == "zigzag":
            # 波線パターン
            for i in range(3):
                offset = i * 10
                pygame.draw.line(screen, WHITE, 
                               (self.x, self.y + offset), 
                               (self.x + self.width, self.y + offset), 2)
        elif self.enemy_type == "shooter":
            # 目のような模様
            eye_size = max(3, self.width // 6)
            pygame.draw.circle(screen, YELLOW, 
                             (int(self.x + self.width * 0.3), int(self.y + self.height * 0.4)), eye_size)
            pygame.draw.circle(screen, YELLOW, 
                             (int(self.x + self.width * 0.7), int(self.y + self.height * 0.4)), eye_size)
        elif self.enemy_type == "elite":
            # 王冠マーク
            pygame.draw.polygon(screen, YELLOW, [
                (self.x + self.width // 2, self.y),
                (self.x + self.width * 0.3, self.y + 10),
                (self.x + self.width * 0.7, self.y + 10)
            ])
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        elif self.enemy_type == "berserker":
            # 角のようなマーク
            pygame.draw.polygon(screen, WHITE, [
                (self.x, self.y + 5),
                (self.x + 5, self.y),
                (self.x + 10, self.y + 5)
            ])
            pygame.draw.polygon(screen, WHITE, [
                (self.x + self.width - 10, self.y + 5),
                (self.x + self.width - 5, self.y),
                (self.x + self.width, self.y + 5)
            ])
        elif self.enemy_type == "sniper":
            # 照準マーク
            center_x = int(self.x + self.width // 2)
            center_y = int(self.y + self.height // 2)
            pygame.draw.circle(screen, WHITE, (center_x, center_y), 8, 2)
            pygame.draw.line(screen, WHITE, (center_x - 12, center_y), (center_x - 8, center_y), 2)
            pygame.draw.line(screen, WHITE, (center_x + 8, center_y), (center_x + 12, center_y), 2)
            pygame.draw.line(screen, WHITE, (center_x, center_y - 12), (center_x, center_y - 8), 2)
            pygame.draw.line(screen, WHITE, (center_x, center_y + 8), (center_x, center_y + 12), 2)
        
        # HPバー
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 5, self.width * hp_ratio, 3))


class Boss:
    """ボスクラス"""
    def __init__(self, difficulty_mod, stage_number=1):
        self.width = 80
        self.height = 80
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = -self.height
        self.target_y = 100  # 登場後の位置
        self.speed = 2
        # ステージが進むほどボスが強くなる
        self.base_hp = 100 + (stage_number - 1) * 50
        self.hp = int(self.base_hp * difficulty_mod["hp"])
        self.max_hp = self.hp
        self.exp_value = int(400 * difficulty_mod["exp"])  # 500から400に減少
        self.stage_number = stage_number
        
        # 移動パターン
        self.move_direction = 1
        self.move_timer = 0
        self.appearing = True  # 登場演出中
        
        # 攻撃パターン（ステージが進むほど攻撃間隔が短くなる）
        self.shoot_timer = 0
        self.shoot_interval = max(50, 100 - stage_number * 8)  # より頻繁に
        self.attack_pattern = 0  # 攻撃パターンのカウンター
        
        # 特殊攻撃用のタイマー
        self.spiral_timer = 0
        self.rapid_fire_timer = 0
        self.wave_timer = 0
        
        # ステージ別のボスデザイン
        self.setup_boss_design()
    
    def setup_boss_design(self):
        """ステージ別のボスデザインを設定"""
        boss_designs = {
            1: {
                "color": (100, 100, 255),      # 青
                "accent": (150, 150, 255),
                "name": "Cosmic Guardian"
            },
            2: {
                "color": (150, 50, 200),       # 紫
                "accent": (200, 100, 255),
                "name": "Void Emperor"
            },
            3: {
                "color": (255, 100, 50),       # オレンジ
                "accent": (255, 150, 100),
                "name": "Mars Titan"
            },
            4: {
                "color": (50, 200, 100),       # 緑
                "accent": (100, 255, 150),
                "name": "Forest Warden"
            },
            5: {
                "color": (255, 50, 50),        # 赤
                "accent": (255, 100, 100),
                "name": "Inferno Lord"
            },
        }
        
        design = boss_designs.get(self.stage_number, boss_designs[1])
        self.color = design["color"]
        self.accent_color = design["accent"]
        self.name = design["name"]
        
    def update(self):
        """ボスの行動更新"""
        # 登場演出
        if self.appearing:
            if self.y < self.target_y:
                self.y += 2
            else:
                self.appearing = False
            return
        
        # 左右移動
        self.move_timer += 1
        if self.move_timer > 60:
            self.move_direction *= -1
            self.move_timer = 0
        
        self.x += self.move_direction * 3
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        
    def shoot(self, bullets, player_x, player_y):
        """ボスの攻撃（複数パターン）"""
        if self.appearing:
            return
            
        self.shoot_timer += 1
        self.spiral_timer += 1
        self.rapid_fire_timer += 1
        self.wave_timer += 1
        
        # 基本攻撃：扇状弾幕
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 4
            
            if self.attack_pattern == 0:
                # パターン1：扇状弾幕（プレイヤーを狙う）
                self._shoot_fan_aimed(bullets, player_x, player_y)
            elif self.attack_pattern == 1:
                # パターン2：円形弾幕
                self._shoot_circle(bullets)
            elif self.attack_pattern == 2:
                # パターン3：レーザー状の直線弾幕
                self._shoot_laser(bullets, player_x, player_y)
            else:
                # パターン4：ランダム散弾
                self._shoot_random(bullets)
        
        # 特殊攻撃1：スパイラル弾幕（常時発動）
        if self.spiral_timer >= 15 and self.stage_number >= 2:
            self.spiral_timer = 0
            self._shoot_spiral(bullets)
        
        # 特殊攻撃2：連射（HPが半分以下で発動）
        if self.hp <= self.max_hp // 2 and self.rapid_fire_timer >= 12:  # 8から12に変更（発射頻度を下げる）
            self.rapid_fire_timer = 0
            self._shoot_rapid_fire(bullets, player_x, player_y)
        
        # 特殊攻撃3：波状攻撃（ステージ3以降）
        if self.wave_timer >= 80 and self.stage_number >= 3:
            self.wave_timer = 0
            self._shoot_wave(bullets)
    
    def _shoot_fan_aimed(self, bullets, player_x, player_y):
        """扇状弾幕（プレイヤーを狙う）"""
        boss_center_x = self.x + self.width // 2
        boss_center_y = self.y + self.height // 2
        
        # プレイヤーへの角度を計算
        dx = player_x - boss_center_x
        dy = player_y - boss_center_y
        base_angle = math.degrees(math.atan2(dy, dx))
        
        bullet_count = 5 + self.stage_number
        spread = 40  # 扇の広がり角度
        
        for i in range(bullet_count):
            angle = base_angle + (i - bullet_count / 2) * (spread / bullet_count)
            rad = math.radians(angle)
            speed_x = math.cos(rad) * 5
            speed_y = math.sin(rad) * 5
            bullets.append(EnemyBullet(boss_center_x, boss_center_y, speed_x, speed_y))
    
    def _shoot_circle(self, bullets):
        """円形弾幕（全方位）"""
        boss_center_x = self.x + self.width // 2
        boss_center_y = self.y + self.height // 2
        
        bullet_count = 12 + self.stage_number * 2
        for i in range(bullet_count):
            angle = (360 / bullet_count) * i
            rad = math.radians(angle)
            speed_x = math.cos(rad) * 4
            speed_y = math.sin(rad) * 4
            bullets.append(EnemyBullet(boss_center_x, boss_center_y, speed_x, speed_y))
    
    def _shoot_laser(self, bullets, player_x, player_y):
        """レーザー状の直線弾幕"""
        boss_center_x = self.x + self.width // 2
        boss_center_y = self.y + self.height // 2
        
        # プレイヤーへの方向
        dx = player_x - boss_center_x
        dy = player_y - boss_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # 5発連続で発射
            for i in range(5):
                speed_x = (dx / distance) * (6 + i * 0.5)
                speed_y = (dy / distance) * (6 + i * 0.5)
                bullets.append(EnemyBullet(boss_center_x, boss_center_y, speed_x, speed_y))
    
    def _shoot_random(self, bullets):
        """ランダム散弾"""
        boss_center_x = self.x + self.width // 2
        boss_center_y = self.y + self.height // 2
        
        bullet_count = 8 + self.stage_number
        for i in range(bullet_count):
            angle = random.uniform(0, 360)
            rad = math.radians(angle)
            speed = random.uniform(3, 6)
            speed_x = math.cos(rad) * speed
            speed_y = math.sin(rad) * speed
            bullets.append(EnemyBullet(boss_center_x, boss_center_y, speed_x, speed_y))
    
    def _shoot_spiral(self, bullets):
        """スパイラル弾幕（回転しながら発射）"""
        boss_center_x = self.x + self.width // 2
        boss_center_y = self.y + self.height // 2
        
        # タイマーを使って回転角度を作る
        angle = (self.spiral_timer * 15) % 360
        rad = math.radians(angle)
        speed_x = math.cos(rad) * 3
        speed_y = math.sin(rad) * 3
        bullets.append(EnemyBullet(boss_center_x, boss_center_y, speed_x, speed_y))
        
        # 反対側にも発射
        rad2 = math.radians(angle + 180)
        speed_x2 = math.cos(rad2) * 3
        speed_y2 = math.sin(rad2) * 3
        bullets.append(EnemyBullet(boss_center_x, boss_center_y, speed_x2, speed_y2))
    
    def _shoot_rapid_fire(self, bullets, player_x, player_y):
        """連射（HP半分以下で発動）"""
        boss_center_x = self.x + self.width // 2
        boss_center_y = self.y + self.height // 2
        
        dx = player_x - boss_center_x
        dy = player_y - boss_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            speed_x = (dx / distance) * 5  # 7から5に減速
            speed_y = (dy / distance) * 5  # 7から5に減速
            bullets.append(EnemyBullet(boss_center_x, boss_center_y, speed_x, speed_y))
    
    def _shoot_wave(self, bullets):
        """波状攻撃（横一列）"""
        boss_center_y = self.y + self.height // 2
        
        # 画面の幅に渡って弾を配置
        bullet_count = 15
        for i in range(bullet_count):
            x = (SCREEN_WIDTH / (bullet_count - 1)) * i
            bullets.append(EnemyBullet(x, boss_center_y, 0, 4))
    
    def draw(self, screen):
        """ボスを描画（ステージ別デザイン）"""
        # ボス本体
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, self.accent_color, (self.x, self.y, self.width, self.height), 3)
        
        # ステージ別の装飾
        if self.stage_number == 1:
            # Stage 1: 宇宙 - 星のマーク
            star_points = [
                (self.x + self.width // 2, self.y + 20),
                (self.x + self.width // 2 + 8, self.y + 35),
                (self.x + self.width // 2 + 20, self.y + 35),
                (self.x + self.width // 2 + 10, self.y + 45),
                (self.x + self.width // 2 + 15, self.y + 60),
                (self.x + self.width // 2, self.y + 50),
                (self.x + self.width // 2 - 15, self.y + 60),
                (self.x + self.width // 2 - 10, self.y + 45),
                (self.x + self.width // 2 - 20, self.y + 35),
                (self.x + self.width // 2 - 8, self.y + 35)
            ]
            pygame.draw.polygon(screen, YELLOW, star_points)
            
        elif self.stage_number == 2:
            # Stage 2: 異次元 - 渦巻きマーク
            center_x = int(self.x + self.width // 2)
            center_y = int(self.y + self.height // 2)
            for i in range(3):
                angle = i * 120
                rad = math.radians(angle)
                end_x = center_x + math.cos(rad) * 25
                end_y = center_y + math.sin(rad) * 25
                pygame.draw.line(screen, self.accent_color, (center_x, center_y), 
                               (int(end_x), int(end_y)), 4)
                
        elif self.stage_number == 3:
            # Stage 3: 火星 - 炎のマーク
            flame_points = [
                (self.x + self.width // 2, self.y + 15),
                (self.x + self.width // 2 + 10, self.y + 30),
                (self.x + self.width // 2 + 5, self.y + 35),
                (self.x + self.width // 2 + 12, self.y + 50),
                (self.x + self.width // 2, self.y + 60),
                (self.x + self.width // 2 - 12, self.y + 50),
                (self.x + self.width // 2 - 5, self.y + 35),
                (self.x + self.width // 2 - 10, self.y + 30)
            ]
            pygame.draw.polygon(screen, YELLOW, flame_points)
            
        elif self.stage_number == 4:
            # Stage 4: ジャングル - 葉のマーク
            leaf_points = [
                (self.x + self.width // 2, self.y + 20),
                (self.x + self.width // 2 + 15, self.y + 40),
                (self.x + self.width // 2, self.y + 60),
                (self.x + self.width // 2 - 15, self.y + 40)
            ]
            pygame.draw.polygon(screen, self.accent_color, leaf_points)
            pygame.draw.line(screen, YELLOW, 
                           (self.x + self.width // 2, self.y + 20),
                           (self.x + self.width // 2, self.y + 60), 3)
            
        elif self.stage_number == 5:
            # Stage 5: 地獄 - 悪魔の角
            horn_left = [
                (self.x + 15, self.y + 20),
                (self.x + 10, self.y + 5),
                (self.x + 20, self.y + 15)
            ]
            horn_right = [
                (self.x + self.width - 15, self.y + 20),
                (self.x + self.width - 10, self.y + 5),
                (self.x + self.width - 20, self.y + 15)
            ]
            pygame.draw.polygon(screen, YELLOW, horn_left)
            pygame.draw.polygon(screen, YELLOW, horn_right)
        
        # 目（共通）
        eye_size = 12
        pygame.draw.circle(screen, YELLOW, (int(self.x + 25), int(self.y + 35)), eye_size)
        pygame.draw.circle(screen, YELLOW, (int(self.x + 55), int(self.y + 35)), eye_size)
        pygame.draw.circle(screen, self.color, (int(self.x + 25), int(self.y + 35)), eye_size // 2)
        pygame.draw.circle(screen, self.color, (int(self.x + 55), int(self.y + 35)), eye_size // 2)
        
        # HPバー（画面上部に大きく表示）
        bar_width = 400
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 50
        
        # 背景
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        # HP
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, self.color, (bar_x, bar_y, bar_width * hp_ratio, bar_height))
        # 枠
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # ボス名
        font_small = pygame.font.Font(None, 28)
        name_text = font_small.render(self.name, True, self.accent_color)
        screen.blit(name_text, (bar_x - name_text.get_width() - 10, bar_y - 2))
        
        # HP数値
        font = pygame.font.Font(None, 32)
        hp_text = font.render(f"{self.hp}/{self.max_hp}", True, WHITE)
        screen.blit(hp_text, (bar_x + bar_width + 10, bar_y - 5))


class EnemyBullet:
    """敵の弾クラス"""
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.speed_x = speed_x
        self.speed_y = speed_y
        
    def update(self):
        """弾の移動"""
        self.x += self.speed_x
        self.y += self.speed_y
        
    def is_off_screen(self):
        """画面外判定"""
        return (self.x < -self.width or self.x > SCREEN_WIDTH or
                self.y < -self.height or self.y > SCREEN_HEIGHT)
    
    def draw(self, screen):
        """弾を描画"""
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.width // 2)


class ExpOrb:
    """経験値オーブクラス"""
    def __init__(self, x, y, exp_value):
        self.x = x
        self.y = y
        self.width = 12
        self.height = 12
        self.exp_value = exp_value
        self.speed_y = 1.5  # 下方向への移動速度
        self.float_timer = 0  # 浮遊アニメーション用
        
    def update(self):
        """オーブの移動"""
        self.y += self.speed_y
        self.float_timer += 1
        # ふわふわと浮遊する動き
        self.x += math.sin(self.float_timer * 0.1) * 0.5
        
    def is_off_screen(self):
        """画面外判定"""
        return self.y > SCREEN_HEIGHT + self.height
    
    def draw(self, screen):
        """オーブを描画"""
        # 外側の光るエフェクト
        glow_size = 16 + int(math.sin(self.float_timer * 0.2) * 2)
        pygame.draw.circle(screen, (100, 200, 255), (int(self.x), int(self.y)), glow_size // 2, 2)
        
        # メインのオーブ
        pygame.draw.circle(screen, (150, 230, 255), (int(self.x), int(self.y)), self.width // 2)
        
        # 中心の輝き
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.width // 4)


class AllyFighter:
    """味方戦闘機クラス"""
    def __init__(self, player, offset_x, offset_y):
        self.player = player
        self.offset_x = offset_x  # プレイヤーからの相対位置X
        self.offset_y = offset_y  # プレイヤーからの相対位置Y
        self.x = player.x + offset_x
        self.y = player.y + offset_y
        self.width = 20
        self.height = 20
        self.shoot_timer = 0
        self.shoot_interval = 30  # プレイヤーより遅い発射間隔
        
    def update(self, bullets):
        """味方機の位置更新と射撃"""
        # プレイヤーの位置に追従
        target_x = self.player.x + self.offset_x
        target_y = self.player.y + self.offset_y
        
        # スムーズに追従
        self.x += (target_x - self.x) * 0.1
        self.y += (target_y - self.y) * 0.1
        
        # 射撃
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            # プレイヤーの半分のダメージ
            damage = max(1, self.player.bullet_damage // 2)
            bullets.append(Bullet(
                self.x + self.width // 2,
                self.y,
                -8,
                damage,
                False,  # 貫通なし
                0,  # ホーミングなし
                0.8,  # やや小さめ
                1.0
            ))
    
    def draw(self, screen):
        """味方機を描画"""
        # 緑色の三角形
        pygame.draw.polygon(screen, GREEN, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        # 白い枠
        pygame.draw.polygon(screen, WHITE, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ], 2)


class Mine:
    """地雷クラス"""
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 15
        self.damage = damage * 3  # プレイヤーの3倍のダメージ
        self.explosion_radius = 60
        self.lifetime = 600  # 10秒間存在
        self.timer = 0
        self.exploded = False
        
    def update(self):
        """地雷の更新"""
        self.timer += 1
        if self.timer >= self.lifetime:
            self.exploded = True
    
    def check_collision(self, enemies):
        """敵との衝突判定"""
        if self.exploded:
            return []
        
        hit_enemies = []
        for enemy in enemies:
            # 地雷の爆発範囲内に敵がいるか
            enemy_center_x = enemy.x + enemy.width // 2
            enemy_center_y = enemy.y + enemy.height // 2
            dist = math.sqrt((enemy_center_x - self.x) ** 2 + (enemy_center_y - self.y) ** 2)
            
            if dist < self.explosion_radius:
                hit_enemies.append(enemy)
                enemy.hp -= self.damage
        
        if hit_enemies:
            self.exploded = True
        
        return hit_enemies
    
    def draw(self, screen):
        """地雷を描画"""
        if self.exploded:
            return
        
        # 点滅効果
        blink = (self.timer // 10) % 2 == 0
        color = RED if blink else (150, 0, 0)
        
        # 地雷本体（六角形）
        center_x = self.x
        center_y = self.y
        radius = self.width // 2
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # 中心の点
        pygame.draw.circle(screen, YELLOW, (int(center_x), int(center_y)), 3)


class Explosion:
    """爆発エフェクトクラス"""
    def __init__(self, x, y, radius=50):
        self.x = x
        self.y = y
        self.max_radius = radius
        self.current_radius = 0
        self.lifetime = 15  # フレーム数
        self.timer = 0
        self.finished = False
        
    def update(self):
        """エフェクトの更新"""
        self.timer += 1
        progress = self.timer / self.lifetime
        self.current_radius = self.max_radius * progress
        
        if self.timer >= self.lifetime:
            self.finished = True
    
    def draw(self, screen):
        """爆発を描画"""
        if self.finished:
            return
        
        progress = self.timer / self.lifetime
        alpha_ratio = 1 - progress
        
        # 外側の円
        color1 = (int(255 * alpha_ratio), int(100 * alpha_ratio), 0)
        pygame.draw.circle(screen, color1, (int(self.x), int(self.y)), int(self.current_radius), 3)
        
        # 内側の円
        if self.current_radius > 10:
            color2 = (int(255 * alpha_ratio), int(200 * alpha_ratio), 0)
            pygame.draw.circle(screen, color2, (int(self.x), int(self.y)), int(self.current_radius * 0.6), 2)


class PowerUpSelectUI:
    """レベルアップ時のパワーアップ選択UI"""
    def __init__(self, is_boss_reward=False, is_epic_reward=False, player=None):
        self.options = []
        self.selected = None
        self.is_boss_reward = is_boss_reward
        self.is_epic_reward = is_epic_reward
        self.selected_index = 0  # キーボード選択用のインデックス
        self.player = player  # プレイヤー情報を保持
        self.generate_options()
        
    def generate_options(self):
        """3つのランダムなパワーアップを生成（レアリティ重み付き、取得済み除外）"""
        if self.is_boss_reward:
            # ボス報酬は均等抽選
            pool = BOSS_REWARD_POOL
            # 取得済みを除外（healは除外しない）
            if self.player:
                filtered_pool = []
                for p in pool:
                    if p["type"] == "heal":
                        filtered_pool.append(p)
                    elif p["type"] not in self.player.acquired_powerups:
                        filtered_pool.append(p)
                    elif p["type"] in self.player.acquired_powerups:
                        # 数値系の比較
                        if p["type"] == "attack_speed":
                            # attack_speedは小さいほど高速
                            if p["value"] < self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                        elif p["type"] in ["movement_speed", "bullet_speed", "bullet_size"]:
                            # その他数値系は大きいほど強力
                            if p["value"] > self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                        else:
                            # レベル制のものは上位レベルなら追加
                            if p["value"] > self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                pool = filtered_pool
            
            if len(pool) >= 3:
                self.options = random.sample(pool, 3)
            else:
                # プールが3未満の場合は全て表示
                self.options = pool
                
        elif self.is_epic_reward:
            # Epic敵報酬：Rare以上のみ抽選
            pool = [p for p in POWERUP_POOL if p["rarity"] in ["rare", "epic"]]
            # 取得済みを除外（healは除外しない）
            if self.player:
                filtered_pool = []
                for p in pool:
                    if p["type"] == "heal":
                        filtered_pool.append(p)
                    elif p["type"] not in self.player.acquired_powerups:
                        filtered_pool.append(p)
                    elif p["type"] in self.player.acquired_powerups:
                        # 数値系の比較
                        if p["type"] == "attack_speed":
                            if p["value"] < self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                        elif p["type"] in ["movement_speed", "bullet_speed", "bullet_size"]:
                            if p["value"] > self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                        else:
                            # レベル制のものは上位レベルなら追加
                            if p["value"] > self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                pool = filtered_pool
            
            if len(pool) >= 3:
                # Rare/Epicの重みを再計算
                weights = [RARITY_CONFIG[p["rarity"]]["weight"] for p in pool]
                # 重み付き抽選で3つ選択
                self.options = random.choices(pool, weights=weights, k=3)
                # 重複を避けるため、同じパワーアップが選ばれた場合は再抽選
                attempts = 0
                while len(set(p["name"] for p in self.options)) < 3 and attempts < 10:
                    self.options = random.choices(pool, weights=weights, k=3)
                    attempts += 1
            else:
                # プールが3未満の場合は全て表示
                self.options = pool
                
        else:
            # 通常パワーアップはレアリティ重み付き抽選
            pool = POWERUP_POOL
            # 取得済みを除外（healは除外しない）
            if self.player:
                filtered_pool = []
                for p in pool:
                    if p["type"] == "heal":
                        filtered_pool.append(p)
                    elif p["type"] not in self.player.acquired_powerups:
                        filtered_pool.append(p)
                    elif p["type"] in self.player.acquired_powerups:
                        # 数値系の比較
                        if p["type"] == "attack_speed":
                            if p["value"] < self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                        elif p["type"] in ["movement_speed", "bullet_speed", "bullet_size"]:
                            if p["value"] > self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                        else:
                            # レベル制のものは上位レベルなら追加
                            if p["value"] > self.player.acquired_powerups[p["type"]]:
                                filtered_pool.append(p)
                pool = filtered_pool
            
            if len(pool) >= 3:
                # 各パワーアップの重みを計算
                weights = [RARITY_CONFIG[p["rarity"]]["weight"] for p in pool]
                # 重み付き抽選で3つ選択（重複なし）
                self.options = random.choices(pool, weights=weights, k=3)
                # 重複を避けるため、同じパワーアップが選ばれた場合は再抽選
                attempts = 0
                while len(set(p["name"] for p in self.options)) < 3 and attempts < 10:
                    self.options = random.choices(pool, weights=weights, k=3)
                    attempts += 1
            else:
                # プールが3未満の場合は全て表示
                self.options = pool
                self.options = random.choices(pool, weights=weights, k=3)
        
        self.selected = None
        self.selected_index = 0
        
    def handle_event(self, event):
        """イベント処理"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # 選択肢のクリック判定
            start_y = 250
            button_width = 700
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            for i in range(len(self.options)):
                button_rect = pygame.Rect(button_x, start_y + i * 120, button_width, 100)
                if button_rect.collidepoint(mouse_x, mouse_y):
                    self.selected = self.options[i]
                    return True
        
        # キーボード操作
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.selected = self.options[self.selected_index]
                return True
            # 数字キーでも選択可能
            elif event.key == pygame.K_1 and len(self.options) >= 1:
                self.selected = self.options[0]
                return True
            elif event.key == pygame.K_2 and len(self.options) >= 2:
                self.selected = self.options[1]
                return True
            elif event.key == pygame.K_3 and len(self.options) >= 3:
                self.selected = self.options[2]
                return True
        
        return False
    
    def draw(self, screen):
        """パワーアップ選択画面を描画"""
        # 半透明の背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # タイトル
        font_large = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 40)
        font_small = pygame.font.Font(None, 28)
        
        if self.is_boss_reward:
            title = font_large.render("BOSS DEFEATED!", True, YELLOW)
            title_glow = font_large.render("BOSS DEFEATED!", True, RED)
            screen.blit(title_glow, (SCREEN_WIDTH // 2 - title_glow.get_width() // 2 + 2, 78))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
            instruction_text = "Choose a BOSS REWARD:"
        elif self.is_epic_reward:
            title = font_large.render("EPIC ENEMY DEFEATED!", True, (255, 215, 0))
            title_glow = font_large.render("EPIC ENEMY DEFEATED!", True, (200, 100, 255))
            screen.blit(title_glow, (SCREEN_WIDTH // 2 - title_glow.get_width() // 2 + 2, 78))
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
            instruction_text = "Choose a RARE REWARD:"
        else:
            title = font_large.render("LEVEL UP!", True, YELLOW)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
            instruction_text = "Choose one power-up:"
        
        instruction = font_small.render(instruction_text, True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 150))
        
        # キーボード操作のヒント
        hint = font_small.render("Use Arrow Keys / W/S + Space, or 1/2/3 to select", True, GRAY)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
        
        # 選択肢を描画
        start_y = 250
        button_width = 700
        button_height = 100
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        
        for i, option in enumerate(self.options):
            button_rect = pygame.Rect(button_x, start_y + i * 120, button_width, button_height)
            
            # ホバー効果とキーボード選択のハイライト
            mouse_pos = pygame.mouse.get_pos()
            rarity = option.get("rarity", "common")
            rarity_color = RARITY_CONFIG[rarity]["color"]
            rarity_name = RARITY_CONFIG[rarity]["name"]
            is_hovered = button_rect.collidepoint(mouse_pos)
            is_keyboard_selected = (i == self.selected_index)
            
            # 背景色と枠線
            if is_hovered or is_keyboard_selected:
                # 選択中の背景（レアリティ色を暗くした色）
                dark_rarity = tuple(int(c * 0.3) for c in rarity_color)
                pygame.draw.rect(screen, dark_rarity, button_rect)
                # 枠線
                border_width = 6 if is_keyboard_selected else 4
                border_color = YELLOW if is_keyboard_selected else WHITE
                pygame.draw.rect(screen, border_color, button_rect, border_width)
            else:
                # 非選択時の背景
                pygame.draw.rect(screen, DARK_GRAY, button_rect)
                pygame.draw.rect(screen, rarity_color, button_rect, 3)
            
            # 番号表示
            number_text = font_medium.render(f"{i+1}", True, YELLOW if (is_hovered or is_keyboard_selected) else GRAY)
            screen.blit(number_text, (button_rect.x - 40, button_rect.y + 35))
            
            # パワーアップ名（レアリティ色）
            name_text = font_medium.render(option["name"], True, rarity_color)
            screen.blit(name_text, (button_rect.x + 20, button_rect.y + 15))
            
            # 説明文
            desc_color = WHITE if (is_hovered or is_keyboard_selected) else GRAY
            desc_text = font_small.render(option["desc"], True, desc_color)
            screen.blit(desc_text, (button_rect.x + 20, button_rect.y + 55))
            
            # レアリティ表示
            rarity_text = font_small.render(f"[{rarity_name}]", True, rarity_color)
            screen.blit(rarity_text, (button_rect.right - rarity_text.get_width() - 10, button_rect.y + 8))


class StageSelectScene:
    """ステージ選択画面"""
    def __init__(self):
        self.current_stage = 1
        self.total_stages = 5
        self.options = []
        self.selected = None
        self.generate_options()
        
    def generate_options(self):
        """選択肢を生成"""
        difficulties = ["Easy", "Normal", "Hard"]
        random.shuffle(difficulties)
        self.options = difficulties[:3]
        
    def handle_event(self, event):
        """イベント処理"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # 選択肢のクリック判定
            start_y = 280
            button_width = 400
            button_height = 80
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            for i, option in enumerate(self.options):
                button_rect = pygame.Rect(button_x, start_y + i * 110, button_width, button_height)
                if button_rect.collidepoint(mouse_x, mouse_y):
                    self.selected = option
                    return True
        return False
    
    def draw(self, screen):
        """ステージ選択画面を描画"""
        screen.fill(BLACK)
        
        # タイトル
        font_large = pygame.font.Font(None, 80)
        font_medium = pygame.font.Font(None, 50)
        font_small = pygame.font.Font(None, 36)
        
        title = font_large.render("Roguelike Shooter", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        
        # ステージ情報
        stage_text = font_medium.render(f"Stage {self.current_stage} / {self.total_stages}", True, YELLOW)
        screen.blit(stage_text, (SCREEN_WIDTH // 2 - stage_text.get_width() // 2, 180))
        
        # 選択肢
        instruction = font_small.render("Select Difficulty:", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 240))
        
        start_y = 280
        button_width = 400
        button_height = 80
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        
        for i, option in enumerate(self.options):
            # ボタン背景
            button_rect = pygame.Rect(button_x, start_y + i * 110, button_width, button_height)
            color = DIFFICULTY_MODIFIERS[option]["color"]
            
            # ホバー効果
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                # ホバー時は明るく
                hover_color = tuple(min(255, c + 50) for c in color)
                pygame.draw.rect(screen, hover_color, button_rect)
                pygame.draw.rect(screen, WHITE, button_rect, 5)
            else:
                pygame.draw.rect(screen, color, button_rect)
                pygame.draw.rect(screen, WHITE, button_rect, 3)
            
            # テキスト
            mod = DIFFICULTY_MODIFIERS[option]
            text = font_medium.render(option, True, BLACK)
            screen.blit(text, (button_rect.centerx - text.get_width() // 2, button_rect.centery - text.get_height() // 2 - 5))
            
            # 詳細情報
            detail = font_small.render(f"HP x{mod['hp']} | EXP x{mod['exp']}", True, WHITE)
            screen.blit(detail, (button_rect.centerx - detail.get_width() // 2, button_rect.bottom + 8))


class GameScene:
    """ゲームプレイ画面"""
    def __init__(self, difficulty, stage_number=1, player_stats=None):
        self.difficulty = difficulty
        self.difficulty_mod = DIFFICULTY_MODIFIERS[difficulty]
        self.stage_number = stage_number
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        
        # プレイヤーの状態を復元（ステージ継続時）
        if player_stats:
            self.player.load_stats(player_stats)
            # 位置だけリセット
            self.player.x = SCREEN_WIDTH // 2
            self.player.y = SCREEN_HEIGHT - 100
        
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []  # 敵の弾
        self.exp_orbs = []  # 経験値オーブ
        self.mines = []  # 地雷
        self.explosions = []  # 爆発エフェクト
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = max(40, 60 - stage_number * 5)  # ステージが進むほど敵の出現が早くなる
        self.game_over = False
        self.victory = False
        
        # レベルアップUI
        self.level_up_ui = None
        self.paused = False
        
        # ボス戦
        self.boss = None
        self.boss_phase = False
        self.enemies_defeated = 0
        
        # ボス出現条件を時間制に変更
        self.boss_timer = 0
        self.boss_appear_time = 60 * 60  # 60秒（60フレーム × 60秒）
        
        # 操作モード（キーボード or マウス）
        self.use_mouse_control = False
        
        # エピックモンスター管理
        self.epic_spawned = 0  # 出現したエピック敵の数
        self.max_epic_per_stage = random.randint(1, 2)  # ステージごとに1~2体
        self.epic_can_spawn_time = 30 * 60  # 30秒後から出現可能
        self.game_time = 0  # ゲーム経過時間
        
        # 背景設定（ステージごとに異なる）
        self.setup_background()
        
    def update(self):
        """ゲーム状態を更新"""
        if self.game_over or self.victory:
            return
        
        # レベルアップUI表示中は一時停止
        if self.paused:
            return
        
        # ゲーム時間をカウント
        self.game_time += 1
        
        # 背景のアニメーション
        self.update_background()
        
        # プレイヤーの移動と射撃
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        # キー入力があればキーボードモード、マウスボタンが押されていればマウスモード
        if any(keys[k] for k in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, 
                                   pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]):
            self.use_mouse_control = False
        elif any(mouse_buttons):
            self.use_mouse_control = True
        
        # 操作モードに応じて移動
        if self.use_mouse_control:
            self.player.move_to_mouse(mouse_pos)
        else:
            self.player.move(keys)
        
        self.player.shoot(self.bullets)
        
        # プレイヤーの能力更新
        self.player.update_orbitals()
        self.player.update_shield_regen()
        
        # 味方機の更新
        for ally in self.player.allies:
            ally.update(self.bullets)
        
        # 地雷の設置
        if self.player.mine_layer:
            self.player.mine_timer += 1
            if self.player.mine_timer >= self.player.mine_interval:
                self.player.mine_timer = 0
                # プレイヤーの位置に地雷を設置
                self.mines.append(Mine(
                    self.player.x + self.player.width // 2,
                    self.player.y + self.player.height // 2,
                    self.player.bullet_damage
                ))
        
        # 地雷の更新と衝突判定
        for mine in self.mines[:]:
            mine.update()
            if mine.exploded or mine.timer >= mine.lifetime:
                if mine in self.mines:
                    self.mines.remove(mine)
            else:
                # 敵との衝突チェック
                hit_enemies = mine.check_collision(self.enemies)
                if hit_enemies:
                    # 地雷が爆発したら爆発エフェクトを追加
                    self.explosions.append(Explosion(mine.x, mine.y, mine.explosion_radius))
        
        # 爆発エフェクトの更新
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.finished:
                self.explosions.remove(explosion)
        
        # 経験値オーブの更新
        for orb in self.exp_orbs[:]:
            orb.update()
            if orb.is_off_screen():
                self.exp_orbs.remove(orb)
            
            # プレイヤーとの接触判定
            if (self.player.x < orb.x + orb.width and
                self.player.x + self.player.width > orb.x and
                self.player.y < orb.y + orb.height and
                self.player.y + self.player.height > orb.y):
                # 経験値獲得
                level_up = self.player.add_exp(orb.exp_value)
                if level_up:
                    self.player.level_up()
                    self.level_up_ui = PowerUpSelectUI(is_boss_reward=False, player=self.player)
                    self.paused = True
                self.exp_orbs.remove(orb)
        
        # 弾の更新（ホーミング対応）
        for bullet in self.bullets[:]:
            bullet.update(self.enemies, self.boss)
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # 敵の弾の更新
        for enemy_bullet in self.enemy_bullets[:]:
            enemy_bullet.update()
            if enemy_bullet.is_off_screen():
                self.enemy_bullets.remove(enemy_bullet)
            
            # プレイヤーとの衝突判定
            if (self.player.x < enemy_bullet.x + enemy_bullet.width and
                self.player.x + self.player.width > enemy_bullet.x and
                self.player.y < enemy_bullet.y + enemy_bullet.height and
                self.player.y + self.player.height > enemy_bullet.y):
                self.player.hp -= 10  # 1から10に変更
                self.enemy_bullets.remove(enemy_bullet)
                if self.player.hp <= 0:
                    self.game_over = True
        
        # ボス戦フェーズ
        if self.boss_phase and self.boss:
            self.boss.update()
            player_center_x = self.player.x + self.player.width // 2
            player_center_y = self.player.y + self.player.height // 2
            self.boss.shoot(self.enemy_bullets, player_center_x, player_center_y)
            
            # ボスとプレイヤー弾の衝突判定
            for bullet in self.bullets[:]:
                if not self.boss:  # ボスが既に倒されている場合はスキップ
                    break
                    
                if (bullet.x < self.boss.x + self.boss.width and
                    bullet.x + bullet.width > self.boss.x and
                    bullet.y < self.boss.y + self.boss.height and
                    bullet.y + bullet.height > self.boss.y):
                    self.boss.hp -= bullet.damage
                    # 貫通弾でない場合は弾を削除
                    if not bullet.piercing and bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    if self.boss.hp <= 0:
                        # ボス撃破！
                        self.boss = None
                        self.boss_phase = False
                        self.victory = True
                        self.level_up_ui = PowerUpSelectUI(is_boss_reward=True, player=self.player)
                        self.paused = True
                        break  # 弾のループを抜ける
            
            # ボスとプレイヤーの衝突
            if self.boss and (self.player.x < self.boss.x + self.boss.width and
                self.player.x + self.player.width > self.boss.x and
                self.player.y < self.boss.y + self.boss.height and
                self.player.y + self.player.height > self.boss.y):
                self.player.hp -= 10  # 1から10に変更
                if self.player.hp <= 0:
                    self.game_over = True
            
            return  # ボス戦中は通常の敵は出現しない
        
        # ボス出現チェック（時間制）
        if not self.boss_phase:
            self.boss_timer += 1
            if self.boss_timer >= self.boss_appear_time:
                self.boss_phase = True
                self.boss = Boss(self.difficulty_mod, self.stage_number)
                self.enemies.clear()  # 既存の敵をクリア
                self.enemy_bullets.clear()  # 敵の弾もクリア
                return
        
        # 敵の生成
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0
            x = random.randint(0, SCREEN_WIDTH - 35)  # 最大サイズに対応
            
            # ステージに応じて敵の種類を選択
            enemy_type = self.choose_enemy_type()
            self.enemies.append(Enemy(x, -35, self.difficulty_mod, self.stage_number, enemy_type))
        
        # 敵の更新
        for enemy in self.enemies[:]:
            enemy.update()
            
            # すべての敵が自機に向けて射撃
            player_center_x = self.player.x + self.player.width // 2
            player_center_y = self.player.y + self.player.height // 2
            enemy.shoot(self.enemy_bullets, player_center_x, player_center_y)
            
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
                
            # プレイヤーとの衝突判定
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                self.player.hp -= 10  # 1から10に変更
                self.enemies.remove(enemy)
                if self.player.hp <= 0:
                    self.game_over = True
        
        # 弾と敵の衝突判定
        for bullet in self.bullets[:]:
            hit_enemy = None
            for enemy in self.enemies[:]:
                if (bullet.x < enemy.x + enemy.width and
                    bullet.x + bullet.width > enemy.x and
                    bullet.y < enemy.y + enemy.height and
                    bullet.y + bullet.height > enemy.y):
                    enemy.hp -= bullet.damage
                    hit_enemy = enemy
                    
                    # 爆発弾の場合、範囲ダメージ
                    if self.player.explosive_bullets:
                        explosion_radius = 50
                        # 爆発エフェクトを追加
                        self.explosions.append(Explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, explosion_radius))
                        
                        for other_enemy in self.enemies[:]:
                            if other_enemy != enemy:
                                dist = math.sqrt((other_enemy.x - enemy.x) ** 2 + 
                                               (other_enemy.y - enemy.y) ** 2)
                                if dist < explosion_radius:
                                    # 距離に応じてダメージ減衰
                                    damage_ratio = 1 - (dist / explosion_radius)
                                    other_enemy.hp -= int(bullet.damage * damage_ratio * 0.5)
                    
                    # 貫通弾でない場合は弾を削除
                    if not bullet.piercing and bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy.hp <= 0:
                        # 敵の位置を保存（ドロップ用）
                        enemy_center_x = enemy.x + enemy.width // 2
                        enemy_center_y = enemy.y + enemy.height // 2
                        
                        # Epic敵を倒した場合の特別報酬
                        is_epic_enemy = enemy.enemy_type in ["elite", "berserker", "sniper"]
                        if is_epic_enemy:
                            # Epic敵を倒したらレベルアップ！
                            self.player.level_up()
                            self.level_up_ui = PowerUpSelectUI(is_boss_reward=False, is_epic_reward=True, player=self.player)
                            self.paused = True
                        
                        # 経験値獲得
                        level_up = self.player.add_exp(enemy.exp_value)
                        self.enemies_defeated += 1
                        
                        # ライフスティール判定
                        if self.player.lifesteal_chance > 0 and random.random() < self.player.lifesteal_chance:
                            self.player.hp = min(self.player.max_hp, self.player.hp + 1)
                        
                        # 10%の確率で経験値オーブをドロップ（Epic敵は50%）
                        orb_chance = 0.5 if is_epic_enemy else 0.1
                        if random.random() < orb_chance:
                            self.exp_orbs.append(ExpOrb(enemy_center_x, enemy_center_y, enemy.exp_value * 2))
                        
                        if level_up and not is_epic_enemy:
                            # 通常レベルアップ（Epic敵では既にレベルアップ済み）
                            self.player.level_up()
                            self.level_up_ui = PowerUpSelectUI(is_boss_reward=False, player=self.player)
                            self.paused = True
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    if not bullet.piercing:  # 貫通弾でなければループを抜ける
                        break
    
    def choose_enemy_type(self):
        """ステージと難易度に応じて敵の種類を選択"""
        # 基本的な敵タイプ
        enemy_types = ["normal", "fast", "tank", "zigzag", "shooter"]
        
        # Epic敵タイプ（3種からランダムで選ぶ）
        epic_pool = ["elite", "berserker", "sniper"]
        
        # Epic敵の出現条件チェック
        can_spawn_epic = (
            self.difficulty in ["Normal", "Hard"] and
            self.game_time >= self.epic_can_spawn_time and
            self.epic_spawned < self.max_epic_per_stage and
            not self.boss_phase
        )
        
        # Epic敵を出現させる（確率制御）
        if can_spawn_epic and random.random() < 0.02:  # 2%の確率
            self.epic_spawned += 1
            return random.choice(epic_pool)
        
        # 通常敵の選択
        # ステージが進むほど強い敵が出やすくなる
        if self.difficulty in ["Normal", "Hard"]:
            # Normal/Hard
            if self.stage_number == 1:
                weights = [70, 18, 5, 5, 2]
            elif self.stage_number == 2:
                weights = [60, 20, 10, 10, 5]
            elif self.stage_number == 3:
                weights = [50, 20, 12, 12, 6]
            elif self.stage_number == 4:
                weights = [40, 20, 15, 10, 15]
            else:  # stage 5
                weights = [30, 20, 15, 15, 20]
        else:
            # Easy: Epic敵なし
            if self.stage_number == 1:
                weights = [70, 20, 5, 5, 0]
            elif self.stage_number == 2:
                weights = [50, 25, 10, 10, 5]
            elif self.stage_number == 3:
                weights = [40, 25, 15, 15, 5]
            elif self.stage_number == 4:
                weights = [30, 25, 20, 15, 10]
            else:  # stage 5
                weights = [20, 25, 20, 20, 15]
        
        return random.choices(enemy_types, weights=weights)[0]
    
    def setup_background(self):
        """ステージごとの背景を設定"""
        # ステージ別の背景色（暗めで邪魔にならない色）
        background_colors = {
            1: (10, 10, 30),      # 濃い青（宇宙）
            2: (20, 10, 25),      # 濃い紫（異次元）
            3: (25, 15, 10),      # 濃い茶色（火星）
            4: (10, 25, 15),      # 濃い緑（ジャングル）
            5: (30, 10, 10),      # 濃い赤（地獄）
        }
        self.bg_color = background_colors.get(self.stage_number, (10, 10, 30))
        
        # 星（小さな装飾）をランダム配置
        self.stars = []
        star_count = 80
        for _ in range(star_count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.choice([1, 1, 1, 2])  # ほとんどが小さい星
            brightness = random.randint(100, 200)
            speed = random.uniform(0.1, 0.5)  # ゆっくり流れる
            self.stars.append({
                "x": x,
                "y": y,
                "size": size,
                "brightness": brightness,
                "speed": speed
            })
    
    def update_background(self):
        """背景をアニメーション"""
        for star in self.stars:
            star["y"] += star["speed"]
            # 画面外に出たら上に戻す
            if star["y"] > SCREEN_HEIGHT:
                star["y"] = 0
                star["x"] = random.randint(0, SCREEN_WIDTH)
    
    def draw_background(self, screen):
        """背景を描画"""
        # 背景色で塗りつぶし
        screen.fill(self.bg_color)
        
        # 星を描画
        for star in self.stars:
            color = (star["brightness"], star["brightness"], star["brightness"])
            if star["size"] == 1:
                screen.set_at((int(star["x"]), int(star["y"])), color)
            else:
                pygame.draw.circle(screen, color, (int(star["x"]), int(star["y"])), star["size"])
    
    def handle_levelup_event(self, event):
        """レベルアップUI中のイベント処理"""
        if self.level_up_ui and self.level_up_ui.handle_event(event):
            # パワーアップが選択された
            selected_powerup = self.level_up_ui.selected
            self.player.apply_powerup(selected_powerup)
            self.level_up_ui = None
            self.paused = False
            return True
        return False
    
    def draw(self, screen):
        """ゲーム画面を描画"""
        # 背景を描画（ステージごとに異なる）
        self.draw_background(screen)
        
        # プレイヤー描画
        self.player.draw(screen)
        
        # 弾描画
        for bullet in self.bullets:
            bullet.draw(screen)
        
        # 敵の弾描画
        for enemy_bullet in self.enemy_bullets:
            enemy_bullet.draw(screen)
        
        # ボス描画
        if self.boss:
            self.boss.draw(screen)
        
        # 敵描画
        for enemy in self.enemies:
            enemy.draw(screen)
        
        # 経験値オーブ描画
        for orb in self.exp_orbs:
            orb.draw(screen)
        
        # 地雷描画
        for mine in self.mines:
            mine.draw(screen)
        
        # 爆発エフェクト描画
        for explosion in self.explosions:
            explosion.draw(screen)
        
        # 味方機描画
        for ally in self.player.allies:
            ally.draw(screen)
        
        # UI描画
        font = pygame.font.Font(None, 32)
        
        # ステージ番号表示
        stage_text = font.render(f"Stage {self.stage_number}/5", True, YELLOW)
        screen.blit(stage_text, (SCREEN_WIDTH - 150, 40))
        
        # HPバー表示
        hp_label = font.render("HP:", True, WHITE)
        screen.blit(hp_label, (10, 10))
        
        # HPバーの枠
        bar_x = 60
        bar_y = 15
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # HPバーの中身（色は残りHPで変化）
        hp_ratio = max(0, self.player.hp / self.player.max_hp)
        current_bar_width = int(bar_width * hp_ratio)
        
        if hp_ratio > 0.6:
            bar_color = GREEN
        elif hp_ratio > 0.3:
            bar_color = YELLOW
        else:
            bar_color = RED
        
        if current_bar_width > 0:
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, current_bar_width, bar_height))
        
        # HP数値表示
        hp_text = font.render(f"{self.player.hp}/{self.player.max_hp}", True, WHITE)
        screen.blit(hp_text, (bar_x + bar_width + 10, 10))
        
        # レベル・経験値表示
        level_text = font.render(f"Level: {self.player.level}", True, WHITE)
        screen.blit(level_text, (10, 45))
        
        exp_text = font.render(f"EXP: {self.player.exp}/{self.player.exp_to_next}", True, WHITE)
        screen.blit(exp_text, (10, 75))
        
        # ボス出現タイマー表示
        if not self.boss_phase:
            remaining_time = max(0, (self.boss_appear_time - self.boss_timer) // 60)
            timer_color = RED if remaining_time <= 10 else YELLOW
            timer_text = font.render(f"Boss in: {remaining_time}s", True, timer_color)
            screen.blit(timer_text, (10, 105))
        
        # 難易度表示
        diff_text = font.render(f"Difficulty: {self.difficulty}", True, self.difficulty_mod["color"])
        screen.blit(diff_text, (SCREEN_WIDTH - 250, 10))
        
        # 操作モード表示
        control_mode = "Mouse" if self.use_mouse_control else "Keyboard"
        control_color = GREEN if self.use_mouse_control else BLUE
        control_text = font.render(f"Control: {control_mode}", True, control_color)
        screen.blit(control_text, (SCREEN_WIDTH - 250, 40))
        
        # ボス警告
        if self.boss_phase and self.boss and self.boss.appearing:
            font_large = pygame.font.Font(None, 72)
            warning_text = font_large.render("BOSS APPROACHING!", True, RED)
            screen.blit(warning_text, (SCREEN_WIDTH // 2 - warning_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # レベルアップUI表示
        if self.level_up_ui:
            self.level_up_ui.draw(screen)
        
        # ゲームオーバー表示
        if self.game_over:
            font_large = pygame.font.Font(None, 72)
            game_over_text = font_large.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            restart_text = font.render("Press R or Click to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        # 勝利表示
        if self.victory and not self.paused:
            font_large = pygame.font.Font(None, 72)
            if self.stage_number >= 5:
                # 最終ステージクリア
                victory_text = font_large.render("ALL STAGES CLEAR!", True, YELLOW)
                screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
                
                congrats_text = font.render("Congratulations!", True, WHITE)
                screen.blit(congrats_text, (SCREEN_WIDTH // 2 - congrats_text.get_width() // 2, SCREEN_HEIGHT // 2))
            else:
                victory_text = font_large.render("STAGE CLEAR!", True, YELLOW)
                screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            restart_text = font.render("Press R or Click to Continue", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))


class Game:
    """ゲームメインクラス"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Roguelike Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # シーン管理
        self.current_scene = "stage_select"
        self.stage_select = StageSelectScene()
        self.game_scene = None
        self.current_stage = 1  # 現在のステージ番号
        self.final_clear = False  # 全ステージクリアフラグ
        
        # プレイヤーの状態を保存（ステージ間で継続）
        self.player_stats = None
        
    async def run(self):
        """メインループ"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            await asyncio.sleep(0)  # pygbag対応
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.current_scene == "stage_select":
                if self.stage_select.handle_event(event):
                    # 難易度が選択されたらゲーム開始
                    selected_difficulty = self.stage_select.selected
                    self.stage_select.current_stage = self.current_stage
                    self.game_scene = GameScene(selected_difficulty, self.current_stage, self.player_stats)
                    self.current_scene = "game"
            
            elif self.current_scene == "game":
                # レベルアップUI中の処理
                if self.game_scene.paused and self.game_scene.level_up_ui:
                    self.game_scene.handle_levelup_event(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        if self.game_scene.game_over:
                            # ゲームオーバーからリスタート（状態をリセット）
                            self.current_stage = 1
                            self.player_stats = None
                            self.stage_select = StageSelectScene()
                            self.stage_select.current_stage = self.current_stage
                            self.current_scene = "stage_select"
                        elif self.game_scene.victory:
                            # ステージクリア後、次のステージへ（状態を保存）
                            self.player_stats = self.game_scene.player.save_stats()
                            self.current_stage += 1
                            if self.current_stage > 5:
                                # 全ステージクリア！
                                self.final_clear = True
                                self.current_scene = "final_clear"
                            else:
                                self.stage_select = StageSelectScene()
                                self.stage_select.current_stage = self.current_stage
                                self.current_scene = "stage_select"
                
                # クリックでも進行可能に
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_scene.game_over:
                        # ゲームオーバーからリスタート（状態をリセット）
                        self.current_stage = 1
                        self.player_stats = None
                        self.stage_select = StageSelectScene()
                        self.stage_select.current_stage = self.current_stage
                        self.current_scene = "stage_select"
                    elif self.game_scene.victory and not self.game_scene.paused:
                        # ステージクリア後、次のステージへ（状態を保存）
                        # pausedがFalseの時のみ（パワーアップ選択中でない時）
                        self.player_stats = self.game_scene.player.save_stats()
                        self.current_stage += 1
                        if self.current_stage > 5:
                            # 全ステージクリア！
                            self.final_clear = True
                            self.current_scene = "final_clear"
                        else:
                            self.stage_select = StageSelectScene()
                            self.stage_select.current_stage = self.current_stage
                            self.current_scene = "stage_select"
            
            elif self.current_scene == "final_clear":
                # 最終クリア画面でクリックまたはRキーでタイトルに戻る
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.current_stage = 1
                    self.player_stats = None
                    self.final_clear = False
                    self.stage_select = StageSelectScene()
                    self.current_scene = "stage_select"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.current_stage = 1
                    self.player_stats = None
                    self.final_clear = False
                    self.stage_select = StageSelectScene()
                    self.current_scene = "stage_select"
    
    def update(self):
        """更新処理"""
        if self.current_scene == "game" and self.game_scene:
            self.game_scene.update()
    
    def draw(self):
        """描画処理"""
        if self.current_scene == "stage_select":
            self.stage_select.draw(self.screen)
        elif self.current_scene == "game" and self.game_scene:
            self.game_scene.draw(self.screen)
        elif self.current_scene == "final_clear":
            self.draw_final_clear()
        
        pygame.display.flip()
    
    def draw_final_clear(self):
        """最終ステージクリア画面を描画"""
        # 背景（黒から金色へのグラデーション風）
        for i in range(SCREEN_HEIGHT):
            ratio = i / SCREEN_HEIGHT
            r = int(10 + (255 - 10) * ratio * 0.3)
            g = int(10 + (215 - 10) * ratio * 0.3)
            b = int(10 + (0 - 10) * ratio * 0.3)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        
        # タイトル
        font_huge = pygame.font.Font(None, 100)
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # "CONGRATULATIONS!"
        title = font_huge.render("CONGRATULATIONS!", True, (255, 215, 0))
        title_shadow = font_huge.render("CONGRATULATIONS!", True, (100, 80, 0))
        screen_center_x = SCREEN_WIDTH // 2
        screen_center_y = SCREEN_HEIGHT // 2
        
        # 影
        self.screen.blit(title_shadow, (screen_center_x - title.get_width() // 2 + 4, 100 + 4))
        # 本体
        self.screen.blit(title, (screen_center_x - title.get_width() // 2, 100))
        
        # "ALL STAGES CLEARED!"
        subtitle = font_large.render("ALL STAGES CLEARED!", True, WHITE)
        self.screen.blit(subtitle, (screen_center_x - subtitle.get_width() // 2, 220))
        
        # 星の装飾
        star_positions = [
            (screen_center_x - 300, 150),
            (screen_center_x + 300, 150),
            (screen_center_x - 350, 220),
            (screen_center_x + 350, 220),
        ]
        
        for pos in star_positions:
            # 星を描画
            star_size = 20
            star_points = []
            for i in range(10):
                angle = (360 / 10) * i - 90
                rad = math.radians(angle)
                radius = star_size if i % 2 == 0 else star_size // 2
                x = pos[0] + math.cos(rad) * radius
                y = pos[1] + math.sin(rad) * radius
                star_points.append((x, y))
            pygame.draw.polygon(self.screen, (255, 215, 0), star_points)
        
        # メッセージ
        messages = [
            "You have conquered all five stages!",
            "The galaxy is safe... for now.",
            "",
            "Thank you for playing!",
        ]
        
        for i, msg in enumerate(messages):
            text = font_medium.render(msg, True, (200, 200, 200))
            self.screen.blit(text, (screen_center_x - text.get_width() // 2, 350 + i * 50))
        
        # 操作説明
        hint = font_small.render("Press R or Click to return to title", True, YELLOW)
        self.screen.blit(hint, (screen_center_x - hint.get_width() // 2, SCREEN_HEIGHT - 80))


async def main():
    """メインエントリーポイント"""
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
