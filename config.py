# config.py
import os

# Telegram Bot Token
BOT_TOKEN = "7893651923:AAF2VrYFQMn3pjek06fti6eTlHFVkj7AUWI"

# Admin User IDs (comma-separated integers)
ADMIN_IDS = [8139558808, 987654321]

# Referral Settings
REFERRAL_REWARD = 5          # Points rewarded to referrer
REFERRED_REWARD = 3          # Points rewarded to new user

# Rate Limiting (seconds)
USER_COOLDOWN = 60           # Per user cooldown between runs

# API Dynamic Configuration (default values – can be changed via admin commands)
DEFAULT_API_CONFIG = {
    "base_url": "https://www.shopsy.in/1.rome/api",
    "offer_name": "Shopsy 30 Coins",
    "platform": "Shopsy",
    "endpoints": {
        "send_otp": "/1/action/view",
        "verify_otp": "/1/action/view",
        "user_state": "/4/user/state",
        "fetch_homepage": "/4/page/fetch",
        "collect": "/1/action/view"
    },
    "headers": {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://www.shopsy.in",
        "Referer": "https://www.shopsy.in/",
        "X-PARTNER-CONTEXT": '{"source":"reseller"}',
        "X-User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36 FKUA/msite/2.0.0/msite/Mobile",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"'
    },
    "payloads": {
        "send_otp": {
            "actionRequestContext": {
                "loginIdPrefix": "+91",
                "loginId": "{phone}",
                "clientQueryParamMap": {
                    "ret": "/",
                    "entryPage": "HEADER_ACCOUNT"
                },
                "loginType": "MOBILE",
                "verificationType": "OTP",
                "screenName": "LOGIN_V4_MOBILE",
                "triggerSna": False,
                "sourceContext": "DEFAULT",
                "type": "LOGIN_IDENTITY_VERIFY"
            }
        },
        "verify_otp": {
            "actionRequestContext": {
                "loginIdPrefix": "+91",
                "loginId": "{phone}",
                "clientQueryParamMap": {
                    "ret": "/",
                    "entryPage": "HEADER_ACCOUNT"
                },
                "loginType": "MOBILE",
                "verificationType": "OTP",
                "screenName": "LOGIN_V4_OTP",
                "churned": False,
                "sourceContext": "DEFAULT",
                "type": "LOGIN",
                "otp": "{otp}",
                "otpRequestId": "{requestId}"
            }
        },
        "user_state": {
            "abDataId": -1
        },
        "fetch_homepage": {
            "pageUri": "/reseller-homepage-store",
            "pageContext": {
                "fetchSeoData": True,
                "pageNumber": 1
            },
            "trackingContext": {},
            "locationContext": {}
        },
        "collect": {
            "actionRequestContext": {
                "pageContext": {
                    "pageNumber": 1.0,
                    "gamificationBUInfoMap": {
                        "COINS-uUFKMoaMyl": {
                            "storePath": [
                                "tyy/4io", "ajy/buh", "tyy/4io", "0pm/fcn/821/a7x/2rv",
                                "0pm/fcn/821/a7x/2si", "0pm/fcn/821/fof", "0pm/0o7",
                                "tyy/4mr/vnf", "tyy/4mr/3nu", "tyy/4mr/tp2", "tyy/4mr/fu6",
                                "tyy/4mr/nkm", "tyy/4mr/q2u", "6bo/tia/8pp/p0w", "6bo/ai3/3oe",
                                "6bo/g0i", "6bo/tia"
                            ],
                            "amount": "10",
                            "rewardType": "COINS",
                            "category": ""
                        },
                        "COINS-Eb4vihNsag": {
                            "storePath": [
                                "eat/ltb", "eat/cpy", "eat/0pt", "eat/xhv", "hlc/etg/sxm",
                                "eat/xgg", "upp/5ix/ymq", "hlc/etg", "hlc/etg"
                            ],
                            "amount": "10",
                            "rewardType": "COINS",
                            "category": ""
                        },
                        "COINS-vxX5IOSbLB": {
                            "storePath": [
                                "tng/clb", "tng/ll1", "tng/dcr", "tng/8k8", "tng/kk6",
                                "tng/sv3", "tng/lhf", "tng/56a", "d69/thr/c4y", "tng/09a",
                                "dgv", "upp/bqi", "upp/3t7", "d69/thr/dkv", "d69/thr/wsp",
                                "tng/cg5", "clo/eof", "clo/odx", "clo/ash/ank/pgi",
                                "clo/cfv/itg/sym", "clo/vua/e8g/fkx", "clo/vua/jlk/4oa",
                                "clo/hlg/nb5", "clo/8on/zpd/ele", "clo/vua/k58/s9z",
                                "clo/vua/mle/y8t", "clo/h4p/2z1/ckv", "clo/qfl/szr/egu",
                                "clo/ash/ohw/otd", "clo/qd8/ezr/uwe", "clo/1hc/kc4/vem",
                                "osp/mba", "osp/mba/o3t/wqv", "osp/mba/erx/k2f",
                                "osp/mba/erx/p4o", "osp/mba/o3t/1q2", "osp/mba/erx/66x",
                                "osp/mba/o3t/1xk"
                            ],
                            "amount": "10",
                            "rewardType": "COINS",
                            "category": ""
                        }
                    }
                },
                "pageUri": "/shopsyrevamp-onboarding-gamification-store?loadoutName=shopsy_onboarding_preferred_category_selection_v2",
                "type": "GAMIFICATION_ALLOCATE_ACTION"
            }
        }
    },
    "auth": {
        "token_extract": ["at", "secureToken", "sn", "secureCookie", "X-Visit-Id"]
    }
}

# Database file
DB_FILE = "viediet.db"

# Logging level
LOG_LEVEL = "INFO"
