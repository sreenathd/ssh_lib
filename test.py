import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock, call
import datetime

sys.modules["pytz"] = MagicMock()
sys.modules["ssl"] = MagicMock()
#sys.modules["CdmRawVaultLoader"] = MagicMock()
sys.modules['cdm_common_utils'] = MagicMock()
sys.modules['cdm_common_utils.vault'] = MagicMock()
sys.modules['cdm_common_utils.vault.vault_utils'] = MagicMock()
sys.modules['cdm_common_utils.aurora'] = MagicMock()
sys.modules['cdm_common_utils.aurora.aurora_utils'] = MagicMock()
sys.modules['cdm_common_utils.redshift'] = MagicMock()
sys.modules['cdm_common_utils.redshift.redshift_utils'] = MagicMock()
sys.modules['cade_common_logging'] = MagicMock()
sys.modules['cade_common_logging.log_object_factory'] = MagicMock()
sys.modules['cade_common_logging.log_type'] = MagicMock()

#from cdm_common_utils.cadm_vault_utils.vault_exception import VaultException

CWD = os.path.abspath(".")
PROJECT_ROOT = os.path.dirname(CWD)
SOURCE_ROOT = os.path.join(CWD, "src/main/cdm_glue/cdm_load_rawvault")
TEST_ROOT = os.path.join(CWD, "src/test/test_cdm_glue_raw_vault_loader")

sys.path.insert(0, TEST_ROOT)

read_audit_csv_name = ""
cur_vault_rec = ""
sys.path.insert(0, SOURCE_ROOT)

import ConstantIO
from parms import Parms
from load_rawvault.load_rawvault import CdmRawVaultLoader


class TestRawVaultLoader(unittest.TestCase):

    args = {
        'metadata_host': "cdm-claims-test1-use1.cluster-cquyej1f3rdh.us-east-1.rds.amazonaws.com",
        'metadata_port': 5432,
        'metadata_db': "cdm",
        'redshift_host': "etcdss-datalake1-test5-use1-rs-camd.cnfw7yh1fsfx.us-east-1.redshift.amazonaws.com",
        'redshift_db': "claims_camd",
        'redshift_port': 5439,
        'redshift_url': "jdbc:redshift://etcdss-datalake1-test5-use1-rs-camd.cnfw7yh1fsfx.us-east-1.redshift.amazonaws.com:5439/claims_camd",
        'vault_schema': 'cdm_vault',
        'bizvault_schema': 'cdm_bizvault',
        'metadata_schema': 'cdm_metadata',
        'stage_schema': 'cdm_staging',
        'data_src_rs_schema': 'cdm_history_copy',
        'param_store_path_aurora': "test/rds_credentials",
        'param_store_path_redshift': "test/redshift_credentials",
        'vault_role': 'cdm-glue-table-builder-test1-use1',
        'team_name': 'cdm',
        'vault_aws_path': "aws-consumer-test",
        'ou': 'test',
        'load_type' : 'delta',
        'lo_tstmp': datetime.datetime(1900, 1, 1, 0, 0, 0, 0),
        'hi_tstmp': datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
    }
    
    def setUp(self):
        args={'src':json.dumps({'load_type':'','tgt_tbl_name':'','domain_name':''})}
        params = Parms(self.args)
        print(params)
        self.crdl = CdmRawVaultLoader(params,args)
        
    def test_metadata_connect(self):
        self.assertTrue(self.crdl.metadata_connect())
        
    def test_vault_connect(self):
        self.assertTrue(self.crdl.vault_connect())
        
    def test_read_audit_valid(self):
        self.crdl.read_audit()
        
    @patch('load_rawvault.load_rawvault.CdmRawVaultLoader.metadata_connect')
    def test_read_audit(self,mock_connect):
        mock_con = mock_connect.return_value
        mock_cur = mock_con.cursor.return_value
        mock_cur.rowcount = 0 
        self.crdl.read_audit()

